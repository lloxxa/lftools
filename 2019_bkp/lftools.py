from __future__ import division
import numpy as np, matplotlib.pyplot as pp
import tools as ts
import autotools as at
import sys
import CONTINWrapper as cw
import pdb
import plottools as pt
import itertools as it
import glob as gl
import matplotlib.colors as cl
import rheotools as rt
import glob as gl
import scipy
import scipy.signal as sg
import fncs as fn
import lmfit as lm

k_B=1.38064852e-23 # m2kgs-2K-1 or JK-1


CONTINPATH="continPY"
cmapc2h=cl.LinearSegmentedColormap.from_list("cold2hot", [(0,0,0.50),(0.9,0.5,0), (1,0,0)])
cmapvir=pp.get_cmap('viridis')
Ttoclr=lambda T,minT,maxT,cmap=cmapc2h: cmap(int((T-minT)*1.0/(maxT-minT+1e-30**(maxT-minT))*255))

class rcycle(object):
	def reset(self):
		self.position=0

	def next(self):
		#print(self.position)
		self.position=self.position+1
		return self.iterable[(self.position-1)%len(self.iterable)]

	def current(self):
		return self.iterable[(self.position-1)%len(self.iterable)]

	def __init__(self, iterable):
		self.iterable=iterable
		self.position=0

mrks=rcycle((".","o","v","P","s","*","+","2","3","4","8","<","p","1","^","h","H",">","x","X","D","d","|","_"))
fldmrks=rcycle(("o","v","P","s","H","X","D"))

clrs=rcycle(['C'+ str(i) for i in range(0,10)]) #these colors are not totally pretty
lnst=rcycle(('-','--','-.',':'))

def open_gpc(filename):
    print(filename)
    with open(filename) as f:
        foundraw=False
        foundhead=False
        datas=[]
        for line in f:
            if foundraw==False:
                splitt=line.split("<")
                if splitt[-1]=="RAW_DATA>\n":foundraw=True
            elif foundraw and not foundhead:
                splithead=line.split("\t")
                foundhead=True
            elif foundraw and foundhead:
                line=line.strip()
                splitt=line.split("\t")
                if len(splitt)>1:
                    datas.append(splitt)
                else:
                    break
    datas=np.array(datas[:-1], dtype='float64')
    return datas



def trapz_ser(series, lims):
    idcs=find_idcs(series, lims)
    return np.trapz(series[idcs[0]:idcs[1],1],series[idcs[0]:idcs[1],0])

def findex(series, value):
    """
    Find idx in series.
    """
    idx=(np.abs(series-value)).argmin()
    return idx


def find_idcs(series, lims):
    """
    Finds indices in the zeroth column of series. Only works for multicolumn arrays,
    as present.
    """
    lims=sorted(lims)
    idc1=np.where(min(abs(series[:,0]-lims[0]))==abs(series[:,0]-lims[0]))[0][0]
    idc2=np.where(min(abs(series[:,0]-lims[1]))==abs(series[:,0]-lims[1]))[0][0]
    idcs=sorted([idc1, idc2])
    return idcs

def simple_baseline(series, xlim):
    """
    series: a two-column array [x y] from which a value will be subtracted
    xlim: extreme values for baseline averageing, [min max]
    """
    xlim=sorted(xlim) # to make it compatible with inverted axes
    idc1=np.where(min(abs(series[:,0]-xlim[0]))==abs(series[:,0]-xlim[0]))[0][0]
    idc2=np.where(min(abs(series[:,0]-xlim[1]))==abs(series[:,0]-xlim[1]))[0][0]
    idcs=sorted([idc1, idc2])
    bali=np.average(series[idcs[0]:idcs[1],1])
    series=np.vstack((series[:,0], series[:,1]-bali)).transpose()

    return series

def oneminus(series):
    """
    series: a two-column array [x y]
    """
    series=np.vstack((series[:,0], -series[:,1]+1)).transpose()
    return series

def flipser(series):
    return np.vstack((series[:,0], -series[:,1])).transpose()

def scaleser(series, factor):
    return np.vstack((series[:,0], series[:,1]*factor)).transpose()

def scalemultiser_int(sdct, skey, xlim):
    idct={key:trapz_ser(sdct[key], xlim) for key in sdct}
    Rdct={key:idct[skey]/idct[key] for key in idct}
    sdct={key:scaleser(sdct[key], Rdct[key]) for key in Rdct}
    return Rdct, sdct, idct

def openALV(filename, find=["\"Correlation\"","\"Count Rate\""]):
	"""
	Written in a stroke of genius. But how does it work?
	"""
	found={i:[] for i in find}
	data=[[]]
	with open(filename) as f:
		for line in f:
			data.append(line.split())
	#print data
	for i in find: #can also be done without a loop, but this is easier to read
		indexi=data.index(i.split())
		indexj=indexi+data[indexi:].index([])
		found[i]=np.array(data[indexi+1:indexj],float)
		#found=False
		#while tofind[i]:
		#for line in data:

	return found

def get_monitor_diode_value(filename):
	with open(filename) as f:
		for line in f:
			if len(line.split())>0:
				if line.split()[0]=="Monitor":
					monitor=line.split()[2]
					break
	return float(monitor)

# TODO: write an object that stores the relevant info for a correlation curve
# 	such as temperature, as the current procedure looses track of the file's identity
#	and only stores the decontextualized data
def openseries(path="",mask="*asc"):
	series=at.Data(path,mask)
	datas={i:openALV(i) for i in series.get_filelist()}
	correlations={j:datas[j][ "\"Correlation\"" ] for j in datas}
	counts={j:datas[j][ "\"Count Rate\"" ] for j in datas}
	condis={j:read_conditions(j) for j in datas}
	return correlations, counts, condis

def openseries_fl(filelist):
	datas={i:openALV(i) for i in filelist}
	correlations={j:datas[j][ "\"Correlation\"" ] for j in datas}
	counts={j:datas[j][ "\"Count Rate\"" ] for j in datas}
	condis={j:read_conditions(j) for j in datas}
	return correlations, counts, condis

def ave_cnts(counts):
	ave_counts=np.average(counts[:,1:2])
	return ave_counts

def checkEqual(iterator):
#	iterator = iter(iterator)
#	try:
#		first = next(iterator)
#	except StopIteration:
#		return True
#
#	return all(first == rest for rest in iterator)
	iterator=np.array(iterator)
	first=iterator[0]
	truth=np.equal(iterator, first)
	if not all(truth):
		print("This is checkEqual reporting. You are probably trying to average sequences\
				of unequal length. Check the amount of datapoints in your files.")
		print("The following iterator content is unequal to the first: \n")
		offense=[i for i in iterator[np.where(truth==False)]]
		print(i)
		return False
	return True

def ave_cor(cordict, keys=[], denominator=1e3):
	# calculates the average over the len(keys) correlation functions in dict cordict
	# unnecessarily retarded way of doing this, but code reusal ftw....
	alldata=[]
	if not keys:
		keys=[i for i in cordict]
	alldata=[cordict[i] for i in cordict]
	nrow,ncol=np.shape(alldata[0])
	shapes=[np.shape(alldata[i]) for i in alldata]
	if not checkEqual(shapes): raise ValueError('Cannot average sequences of unequal length. Clean up the files.')

	ave=np.array([[sum(i[k,j] for i in alldata)/len(keys) for j in range(0,ncol) ] for k in range(0,nrow)])
	ave[:,0]=ave[:,0]/denominator
	return ave

def ave_dct_minidx(dct):
	"""
	Averages a dict of a:[(x, f(x)) for x ix xs], with only x that are present in all members of the dict.
	"""
	minset=np.array(dct[dct.keys()[0]][:,0])
	for a in dct:
		minset=np.array([idp for idp in minset if idp in dct[a][:,0]])
	dct_arrays={a:dict(dct[a]) for a in dct}
	avgs=np.array([[i,sum([dct_arrays[a][i]/len(dct) for a in dct])] for i in minset])
	return avgs

def ave_dct_maxidx(dct):
	"""
	Averages a dict of a:[(x, f(x)) for x ix xs], with all x that are present in all members of the dict.
	"""
	allidx=np.hstack([dct[a][:,0] for a in dct])
	maxset=set(allidx)
	dct_arrays={a:dict(dct[a]) for a in dct}
	toavg={i:[dct_arrays[a][i] for a in dct if i in dct_arrays[a]] for i in maxset}
	avgs=np.array([[i, np.average([toavg[i]])] for i in sorted(toavg.keys())])
	return avgs

def q(r_idx, theta, lambd0):
	return (4*np.pi*r_idx*np.sin(theta*0.5))/lambd0

def gamma_to_D(gammas, q):
	# checked against AfterALV output. Also check against ALV software.
	return np.array([gamma/(q**2) for gamma in gammas])

def gamma_to_R(gammas, T, q, eta, k=1.38064852e-23):
	# checked against AfterALV output. Also check against ALV software.
	return np.array([(k*T*q**2)/(6*np.pi*eta*gamma) for gamma in gammas])

def D_to_R(Ds, T, q, eta, k=1.38064852e-23):
	# has not been checked against AfterALV output.
	return np.array([(k*T)/(6*np.pi*eta*D) for D in Ds])

def renorm_wtc(xdata, ydata):
	"""
	Renormalizes weights to concentrations.	Returns a two-column array.

	W 2017.29.02 // Aljosha
	renorm_wtc(xdata, ydata) returns np.array(xdata, ydata)
	with the ydata renormalized according to AfterALVs "HocusPocus"
	routine """
	renorm_xy=[]
	for i in range(1, len(xdata)): # this is unpythonic. think about it.
		x1=xdata[i]
		x2=xdata[i-1]
		y1=ydata[i]
		y2=ydata[i-1]
		x12=x1/x2
		dx=x1-x2
		yh=dx*0.5*(y1+y2)
		renorm_xy.append([0.5*(x1+x2), yh/(np.log10(x12))])
	return np.array(renorm_xy)

def open_mc(filename, nc=2):
	data=[[]]
	with open(filename) as f:
		cnt=1
		for line in f:
			words=line.split()
			if len(words)!=nc:
				print("Skipping line n=%i"%(cnt))
			if len(words)==nc:
				data.append([float(i) for i in words])
			cnt+=1
	data=np.array(data[1:len(data)])
	return(data)

def screen_dir(path="", mask="*asc"):
	# data clean-up
	pp.ion()
	pp.figure()

	[corfs, counts, condis]=openseries(path, mask)
	av_counts=np.array([[int(i[:-4]), np.average( [ counts[i][:,1]  ] )] for i in counts])
	pp.plot(av_counts[:,0], av_counts[:,1], 'x')
	pp.ylabel("Average count rate")
	pp.xlabel("Experiment number")
	pp.title("Count rate average")

	pp.figure()
	lbldict={i:i for i in counts}
	datadict={i:counts[i][:,0:2] for i in counts}
	ts.plot_series_from_dict(datadict, lbldict)
	pp.xlabel("Time (s)")
	pp.ylabel("Count rate 1 (kHz)")
	pp.title("Count rates")

	pp.figure()
	lbldidt={i:i for i in corfs}
	datadict={i:corfs[i][:,(0,2)] for i in corfs}
	ts.plot_series_from_dict(datadict, lbldict)
	pp.xlabel("Time (s)")
	pp.ylabel("$g_1$")
	pp.title("Field correlation functions")

def contin_dir(path="", mask="*.asc", paramfile="/Users/aljosha/lfscripts/pyCONTIN/dev/pbparam.txt", filestring="lfcontin"):
	[corfs, counts, condis]=openseries(path, mask)
	q=condis[condis.keys()[0]]["q"]
	r_idx=condis[condis.keys()[0]]["r_idx"]
	T=np.average([condis[i]["T"] for i in condis])
	eta=np.average([condis[i]["eta"] for i in condis])

	# TODO add a routine that documents contributors to the average
	meancorf=ave_cor(corfs)
	cnt_out=cw.runCONTINfit(meancorf[:,0], meancorf[:,2], paramfile)
	chosen_sol_parameters=cnt_out[-1][0]
	chosen_sol=cnt_out[-1][1]
	chosen_sol_wtc=renorm_wtc(chosen_sol[:,2], chosen_sol[:,0])
	Ds=gamma_to_D(chosen_sol_wtc[:,0], q)
	Rs=gamma_to_R(chosen_sol_wtc[:,0], T, q, eta)*1e9 #we're going for nanometers

	# TODO add a routine that puts all the relevant parameters in a text file
	# T, q, nm.
	condistring="T={:1.12e} q={:1.12e} eta={:1.12e} r_idx={:1.12e} \n".format(T,q,eta,r_idx)
	headerstring="Gamma (s^-1)       R (nm)       D (m^2.s^-1)        Amplitude         Weighted amplitude"

	output=np.array([[chosen_sol_wtc[i,0], Rs[i], Ds[i], chosen_sol[i][0], chosen_sol_wtc[i,1]  ] for i in range(0,len(chosen_sol_wtc))])
	np.savetxt(filestring+".lf.out", output, header=condistring+headerstring)

	return chosen_sol


def read_conditions(ascpath):
	condis={}
	with open(ascpath) as f:
		for line in f:
			words=line.split()
			if words:
				if words[0]=="Temperature":condis["T"]=float(words[-1])
				elif words[0]=="Viscosity":condis["eta"]=float(words[-1])*1e-3
				elif words[0]=="Refractive":condis["r_idx"]=float(words[-1])
				elif words[0]=="Angle":condis["Theta"]=float(words[-1])
				elif words[0]=="Wavelength":condis["lambda0"]=float(words[-1])*1e-9
				elif words[0]=="MeanCR0":condis["MeanCR0"]=float(words[-1])
				elif words[0]=="MeanCR1":condis["MeanCR1"]=float(words[-1])
#				elif words[0]=="Mode":condis["Mode"]=" ".join(words[2:])[1:-2]
			if len(condis)==7: break
		else:
			print("Could not find experimental conditions in the input! Expect the unexpected..")
	condis["q"]=4*np.pi*condis["r_idx"]*np.sin(np.pi*(condis["Theta"]/180.)/2.)/condis["lambda0"]
	if "MeanCR1" in condis: condis["MeanCR"]=np.average([condis["MeanCR0"], condis["MeanCR1"]])
	return condis

def plot_series_from_dict(dict_q2ser, dict_q2lbl, output_file=None, clrs=['b','g','r','c','m','y','k'], xlog=True, ylog=False):
        markers=['o','v','^','s','p','>','<','*','.','1','2','3']
        q_sorted=sorted([q for q in dict_q2ser])
        for i in range(0,len(q_sorted)):
#                if q_sorted[i][-2:]=='20': clr='b'
#                elif q_sorted[i][-2:]=='50': clr='r'
                clr=clrs[i%len(clrs)]
                if q_sorted[i][22:25]=="0o0": sbl='o'
                elif q_sorted[i][22:25]=="0o1": sbl='x'
                elif q_sorted[i][22:25]=="0o5": sbl='s'
                elif q_sorted[i][22:25]=="1o5": sbl='*'
                data=dict_q2ser[q_sorted[i]]
                lbl=dict_q2lbl[q_sorted[i]]
                pp.plot(data[:,0], data[:,1], marker=sbl, \
                label=lbl, markeredgecolor=clr, color=clr, linewidth=1, markersize=10, markerfacecolor='none', markeredgewidth=1.5)
        pp.legend()
##
def plot_series_from_dict_br(dict_q2ser, dict_q2lbl, output_file=None, xlog=True, ylog=False):
        markers=['o','v','^','s','p','>','<','*','.','1','2','3']
        q_sorted=sorted([q for q in dict_q2ser])
        for i in range(0,len(q_sorted)):
                if q_sorted[i][-2:]=='20': clr='b'
                elif q_sorted[i][-2:]=='50': clr='r'
                if q_sorted[i][22:25]=="0o0": sbl='o'
                elif q_sorted[i][22:25]=="0o1": sbl='x'
                elif q_sorted[i][22:25]=="0o5": sbl='s'
                elif q_sorted[i][22:25]=="1o5": sbl='*'
                data=dict_q2ser[q_sorted[i]]
                lbl=dict_q2lbl[q_sorted[i]]
                pp.plot(data[:,0], data[:,1], marker=sbl, \
                label=lbl, markeredgecolor=clr, color=clr, linewidth=1, markersize=10, markerfacecolor='none', markeredgewidth=1.5)
        pp.legend()
##
def plot_series_from_dict_ocd(datasdict, labeldict, colordict=None, markerdict=None, order_to_key=None, weed=1,**kwargs):
        """
        OCD-proof version for the classic plot_series_from_dict. Supply markers, labels, colors,
        and, optionally, an order for all the series. One series per key/series pair.
        Future: modify plotting towards a true OO-style.
        """
        if colordict==None: colordict={key:clrs.next() for key in datasdict}
        if markerdict==None: markerdict={key:mrks.next() for key in datasdict}
        if order_to_key==None: order_to_key=[key for key in datasdict]
        for key in order_to_key:
                print(key)
                pp.plot(datasdict[key][::weed,0],datasdict[key][::weed,1], c=colordict[key],\
                    marker=markerdict[key], label=labeldict[key], **kwargs)
##

def plot_series_from_dict_short(datasdict, labeldict, shortdict, order_to_key=None, weed=1, **kwargs):
        """
        20170831 Alexei
        Useful to have ordered legends with the plotting conditions supplied via the 'short'
        pyplot conventions.
        """
        if order_to_key==None: order_to_key=[key for key in datasdict]
        for key in order_to_key:
                print(key)
                pp.plot(datasdict[key][::weed,0], datasdict[key][::weed,1], shortdict[key],\
                        label=labeldict[key], **kwargs)
##

def plot_series_from_dict_ordered(datasdict, labeldict, order_to_key=None, weed=1,
        mrks=mrks, **kwargs):
        """
        20170831 Alexei
        Useful to have ordered legends with the plotting conditions supplied via the 'short'
        pyplot conventions.
        """
        if order_to_key==None: order_to_key=[key for key in datasdict]
        for key in order_to_key:
                print(key)
                pp.plot(datasdict[key][::weed,0], datasdict[key][::weed,1], marker=mrks.next(),\
                        label=labeldict[key], **kwargs)
##

def labels(xlabel=None, ylabel=None, title=None, fontsize=20, xlog=True, ylog=False, xlim=None, ylim=None):
	if xlog: pp.xscale('log')
	if ylog: pp.yscale('log')
	if title: pp.title(title, fontsize=fontsize, y=0.93)
	if xlabel: pp.xlabel(xlabel, fontsize=fontsize)
	if ylabel: pp.ylabel(ylabel, fontsize=fontsize)
	if xlim: pp.xlim(xlim[0],xlim[1])
	if ylim: pp.ylim(ylim[0],ylim[1])

def twinplot(xdata, y1data, y2data, ax1_opts, ax2_opts,	xlabel='', y1label='', y2label='', title=''):
	# TODO add labeling and formating support
	# maybe that'll mean writing formatting functions that work purely on the axes/figures objects
	fig=pp.figure()
	ax1=fig.add_subplot(111)
	ax2=ax1.twinx()

	g1=ax1.plot(xdata,y1data,**ax1_opts)
	g2=ax2.plot(xdata,y2data,**ax2_opts)
	graphs=g1+g2

	ax1.set_xlabel(xlabel)
	ax1.set_title(title)
	ax1.set_ylabel(y1label)
	ax2.set_ylabel(y2label)
	pp.show()
	return fig, graphs, [ax1,ax2]

def smooth(data, binsize):
	box = np.ones(binsize)/binsize
	y_smooth=np.convolve(data, box, mode='same') # how does this work???
	return y_smooth

def read_condis_header(header, condis, split_token=' '):
	"""
	29/03/2017. LF.
	Takes a header with condi=<some value>, and the statements separated by split_token.
	Returns a dict with condi:<some value>.
	"""
	extract_value=lambda lst, condi: [head[head.find(condi)+len(condi):] \
		for head in lst if head.find(condi)!=-1][0]
	headerlst=header.split(split_token)
	return {condi[:-1]:np.float(extract_value(headerlst, condi)) for condi in condis}

def get_heads(file_list, linenr=1):
        heads={}
        for i in file_list:
                with open(i) as fl:
                        for j in xrange(linenr): heads[i]=fl.readline()
        return heads

class CorAnalysis(object): 
	"""
	Class based on object to store a given collection of correlation functions. Drives contin analysis
	with the pyCONTIN wrapper.
	def __init__(self, file_list, counts, ave_Ts, condis, corfs, rng):
	"""

	def set_file_list(self, file_list):
		self.file_list=file_list

	def get_file_list(self):
		return self.file_list

	def set_counts(self, counts):
		self.counts=counts

	def get_counts(self):
		return self.counts

	def set_ave_Ts(self, ave_Ts):
		self.ave_Ts=ave_Ts

	def get_ave_Ts(self):
		return self.ave_Ts

	def set_condis(self, condis):
		self.condis=condis

	def get_condis(self):
		return self.condis

	def set_corfs(self, corfs):
		self.corfs=corfs

	def get_corfs(self):
		return self.corfs

	def set_check(self, check):
		self.check=check

	def get_check(self):
		return self.check

	def set_corf(self, corf):
		self.corf=corf

	def get_corf(self):
		return self.corf

	def set_ave_condis(self, ave_condis):
		self.ave_condis=ave_condis

	def get_ave_condis(self):
		return self.ave_condis

	def set_rng(self, rng):
		self.rng=rng

	def get_rng(self):
		return self.rng

	def set_chosen_sol(self, chosen_sol):
		self.chosen_sol=chosen_sol

	def get_chosen_sol(self):
		return self.chosen_sol

	def set_chosen_sol_pars(self, chosen_sol_pars):
		self.chosen_sol_pars=chosen_sol_pars

	def get_chosen_sol_pars(self):
		return self.chosen_sol_pars

	def set_continout(self, continout):
		self.continout=continout

	def get_continout(self):
		return self.continout

	def get_corints(self):
		return self.corints

	def get_runNs(self):
		return self.runNs

	def averg_condis(self):
		condis=self.get_condis()
		check=self.get_check()
		keys=[ key for key in condis[condis.keys()[0]]]
		ave_condis={key:np.average( np.array([ condis[filename][key] for filename in condis if check[filename]==True ]) ) for key in keys }
		self.set_ave_condis(ave_condis)

	def check_cor_integral(self, abs_corr_threshold=1.1, frac_int_threshold=0.8):
		corfs=self.get_corfs()
		check=self.get_check()
		corints={c:np.trapz(corfs[c][np.where(corfs[c][:,1]>1),1], corfs[c][np.where(corfs[c][:,1]>1),0]) for c in corfs}
		self.corints=corints

		for c in check:
			if np.any(corfs[c][:,1]>abs_corr_threshold):
				print("File {} exceeds correlation threshold of {} and is disabled".format(c, abs_corr_threshold))
				check[c]=False

		average_int=np.average([corints[c] for c in corints if check[c]==True])
		for c in check:
			if abs(corints[c]-average_int)>frac_int_threshold*average_int:
				print("File {} exceeds correlation integral threshold and is disabled".format(c))
				check[c]=False

		self.set_check(check)

	def check_count_rates(self, binsize, threshold_frac, mean_tolerance_frac):
		# it would be nice if it would be easy to re-run this function with different tolerance settings
		# to play with the data
		# TODO - seperate plotting commands from the functional body of the function to improve
		# readibility. As we speak, it is a mess.
		counts=self.get_counts()
		Nfiles=len(counts)

		averuncnt=np.average(np.hstack([counts[filename][:,1] for filename in counts]))

		avecnts={ filename: np.average(counts[filename][:,1]) for filename in counts }
		avg_fig=pp.figure()
		avg_ax1=avg_fig.add_subplot(1,1,1)
		avg_ax1.axhline(averuncnt, label="Average over all files", lw=3, color='c')

		check={filename:True for filename in counts} # files are accepted by default

		pp.figure()
		clrs=pp.get_cmap('brg')
		maxcnt=max(avecnts.viewvalues()); mincnt=min(avecnts.viewvalues()); avebw=maxcnt-mincnt
		if abs(avebw)<0.00001: avebw=mincnt
		pp.axhline(averuncnt*(1-threshold_frac), lw=2, c=clrs(128))
		pp.axhline(averuncnt*(1+threshold_frac), lw=2, c=clrs(128))
		for filename in counts:
			avecnt=np.average(counts[filename][:,1])
			# check if the average deviates more than mean_tolerance_frac
			if abs(avecnt-averuncnt)>mean_tolerance_frac*averuncnt:
				check[filename]=False
				print("File {} exceeds mean counts tolerance and is disabled".format(filename))
				clrcode=128; marker='X'
			# check if there are spikes of more than threshold_frac
			elif True in (abs(counts[filename][:,1]-averuncnt)>averuncnt*threshold_frac):
				check[filename]=False
				print("File {} exceeds absolute count tolerance and is disabled".format(filename))
				clrcode=128; marker='x'
			else:
				clrcode=(avecnt-mincnt)/avebw*255; marker='o'
				check[filename]=True
			# end if
			pp.scatter(counts[filename][:,0],counts[filename][:,1], label='{:d}'.format(int(filename[:-4])), \
			s=50, c=clrs(int(clrcode)), alpha=0.5, lw=1.5, marker=marker)
			[avg_ax1.scatter(int(filename[:-4]), avecnts[filename], marker=marker, s=50, \
					alpha=0.7, lw=1.5, c=clrs(int(clrcode)))]
			pp.legend()
			#print "Filename: {}, average counts: {:f}, color coded: {:f}".format(filename, avecnt, clrcode)
			#print "Counts must run between {:f} and {:f}".format(avecnt*(1-threshold_frac), avecnt*(1+threshold_frac))
		avg_ax1.legend()
		self.set_check(check)

	def continfit(self, continpath=CONTINPATH, \
			paramfile="/Users/aljosha/Dropbox/PCC-PhD/Scripts/pbparam-dynagmnmx.param", filestring="lfcnt"):
		"""
		Feeds the averaged correlation out of the object into contin (ran from continpath)
		"""
		T,q,eta,r_idx=[self.get_ave_condis()[i] for i in ['T','q','eta','r_idx']]
		frame0, frame1=self.get_rng()
		filestring+='{:.0f}-{:.0f}T{:.0f}'.format(self.get_rng()[0], self.get_rng()[1], self.get_ave_condis()['T'])
		corf=self.get_corf()
		continout=cw.runCONTINfit(corf[:,0], corf[:,1], paramfile, filestring+'.cntin', filestring+'.cntout')
		self.set_continout=continout

		chosen_sol_pars=continout[-1][0]
		chosen_sol=continout[-1][1]
		chosen_sol_wtc=renorm_wtc(chosen_sol[:,2], chosen_sol[:,0])
		Ds=gamma_to_D(chosen_sol_wtc[:,0], q)
		Rs=gamma_to_R(chosen_sol_wtc[:,0], T, q, eta)*1e9 #we're going for nanometers

		condistring="T={:1.12e} q={:1.12e} eta={:1.12e} r_idx={:1.12e} frame0={:.0f} framei={:.0f} \n"\
				.format(T,q,eta,r_idx,frame0,frame1)
		headerstring="Gamma (s^-1) \t R (nm) \t D (m^2.s^-1) \t Amplitude \t Weighted amplitude"

		output=np.array([[chosen_sol_wtc[i,0], Rs[i], Ds[i], chosen_sol[i][0], \
				chosen_sol_wtc[i,1]  ] for i in range(0,len(chosen_sol_wtc))])
		np.savetxt(filestring+".lf.out", output, header=condistring+headerstring)

		self.set_chosen_sol(chosen_sol)
		self.set_chosen_sol_pars(chosen_sol_pars)

		# but why
		return None

	def ave_cors(self, check, denominator=1):
		file_list=self.get_file_list()
		corfs=self.get_corfs()
		alldata=[corfs[filename] for filename in file_list if check[filename]==True]
		# check if all corfs have the same amount of rows. Raise an exception if not.
		nrowsdict={filename:len(corfs[filename]) for filename in file_list if check[filename]==True}
		nrowslist=[nrowsdict[filename] for filename in nrowsdict]
		if np.size(np.unique(nrowslist))!=1:
			print("Correlation files in range {} have no unique sample count")
			print("It is probably advisable to remove the offending file. I'll raise an exception.")
			print(nrowsdict)
			raise IOError
		nrow,ncol=np.shape(alldata[0])
		average_of_correlations=np.array\
			([[sum(i[k,j] for i in alldata)/len(alldata) for j in range(0,ncol) ]\
			for k in range(0,nrow)])
		self.set_corf(average_of_correlations)
		self.averg_condis()

	def correct_s_to_ms(self, factor=0.001, time_idx=0):
		# ugly. Might be rewritten with hstack.
		corfs=self.get_corfs()
		for filename in corfs:
			corf=corfs[filename]
			corf[:,time_idx]=corf[:,time_idx]*factor
			corfs[filename]=corf
		self.set_corfs(corfs)

	def plot_corf(self):
		pp.figure()
		corfs=self.get_corfs()
		avecorf=self.get_corf()
		[pp.scatter(corfs[filename][:,0],corfs[filename][:,1], label=filename, marker=mrks.next()) for filename in corfs]
		pp.plot(avecorf[:,0],avecorf[:,1], label="Average", lw=1)
		pp.xlabel("$t$ (s)")
		pp.ylabel("Correlation")
		pp.legend()

	def plot_checked_corf(self):
		pp.figure()
		corfs=self.get_corfs()
		avecorf=self.get_corf()
		check=self.get_check()
		[pp.scatter(corfs[filename][:,0],corfs[filename][:,1], label=filename, marker=mrks.next()) for filename in corfs if check[filename]==True]
		[pp.scatter(corfs[filename][:,0],corfs[filename][:,1], label=filename, marker='X', color='red', facecolor='None', linewidths=0.3) for filename in corfs if check[filename]==False]
		pp.plot(avecorf[:,0],avecorf[:,1], label="Average", lw=1)
		pp.legend()

	def write_avg(self):
		corf=self.get_corf()
		condis=self.ave_condis
		T=condis['T']
		q=condis['q']
		Theta=condis['Theta']
		MeanCR=condis['MeanCR0']
		rsccorf=np.vstack([corf[:,0], corf[:,1], corf[:,1]/corf[0,1]]).transpose()
		Tround=int(self.ave_Ts)
		filename="g2min1-T{}.avg".format(Tround)
		f=open(filename, mode='w')
		head="File generated by object of CorAnalysis class, method write_avg. \n T={}, q={}, Theta={}, MeanCR={} \n tau(s) g2-1 (g2-1)/(g2-1)(t=0)".format(T,q,Theta,MeanCR)
		np.savetxt(f, rsccorf, header=head)
		f.close()

	def plot_corints(self):
		pp.figure()
		corints=self.get_corints()
		check=self.get_check()
		runNs=self.get_runNs()

		[pp.scatter(runNs[filename], corints[filename], marker=check[filename]*'o'+(not(check[filename]))*'X') for filename in corints]
		pp.xlabel("Run number")
		pp.ylabel("Integral correlation")
		pp.legend()

	def set_runNs(self):
		condis=self.get_condis()
		self.runNs={c:int(c[:-4]) for c in condis}

	def __init__(self, file_list, counts, ave_Ts, condis, corfs, rng):
		self.set_file_list(file_list)
		self.set_counts(counts)
		self.set_ave_Ts(ave_Ts)
		self.set_condis(condis)
		self.set_corfs(corfs)
		self.set_rng(rng)
		self.set_runNs()

class CorAverager(CorAnalysis):
	"""
	Class CorAverager based on CorAnalysis, inherits full constructor.
	More suited to non-CONTIN analysis such as microrheology
	def __init__(self, file_list, counts, ave_Ts, condis, corfs, rng)
	06.11'19///SLAYER
	"""
	def set_fit_rsls(self, rsls):
		self.fit_rsls=rsls

	def get_fit_rsls(self):
		return self.fit_rsls

	def set_sqrtg2min1(self, sqrtg2min1):
		self.sqrtg2min1=sqrtg2min1

	def get_sqrtg2min1(self):
		return self.sqrtg2min1

	def set_nmz_corfs(self, nmz_corfs):
		self.nmz_corfs=nmz_corfs

	def get_nmz_corfs(self):
		return self.nmz_corfs

	def get_avg_nmz_corf(self):
		return self.avg_nmz_corf

	def set_avg_nmz_corf(self, avg_nmz_corf):
		self.avg_nmz_corf=avg_nmz_corf

	def get_chkd_corfs(self):
		return self.chkd_corfs

	def set_chkd_corfs(self, chkd_corfs):
		self.chkd_corfs=chkd_corfs

	def get_msd(self):
		return self.msd

	def set_msd(self, msd):
		self.msd=msd

	def get_G(self):
		return self.G

	def set_G(self, G):
		self.G=G

	def _sqrt_corfs(self, tolerance=1e-30):
		corfs=self.get_chkd_corfs()
		corfs={a:corfs[a][np.where(corfs[a][:,1]>tolerance)] for a in corfs}
		sqrtg2min1={a:np.vstack([corfs[a][:,0], np.sqrt(corfs[a][:,1])]).transpose() for a in corfs}
		self.set_sqrtg2min1(sqrtg2min1)

	def _fit_corfs_strexp(self, fit_uptocor):
		sqrtg2min1=self.get_sqrtg2min1()
		tofit={a:chopy(sqrtg2min1[a], (fit_uptocor, 1.1)) for a in sqrtg2min1}
		A_ests={a:np.average(sqrtg2min1[a][:3,1] ) for a in sqrtg2min1}
		betaA_ests={a:sqrtg2min1[a][findex(sqrtg2min1[a][:,1], fit_uptocor),0]**(-1)/20 for a in sqrtg2min1}
		print(betaA_ests)
		p={a:lm.Parameters() for a in sqrtg2min1}
		for a in p:
			p[a].add_many(('A', A_ests[a], True, 0.65, 1.0),
				      ('beta', betaA_ests[a], True, 0.0200, 50000),
				      ('stretch', 0.85, True, 0.7, 1))
		print(p)
		rsls={a:lm.minimize(fn.stretchexp, p[a], args=[tofit[a][:,0], tofit[a][:,1]]) for a in sqrtg2min1}
		self.set_fit_rsls(rsls)

	def _nmz_corfs(self):
		corfs=self.get_sqrtg2min1()
		rsls=self.get_fit_rsls()
		nmz_corfs={a:np.vstack([corfs[a][:,0], corfs[a][:,1]/rsls[a].params['A'].value]).transpose() for a in corfs}
		self.set_nmz_corfs(nmz_corfs)

	def _select_corfs(self):
		chk=self.get_check()
		corfs=self.get_corfs()
		chkd_corfs={a:corfs[a] for a in corfs if chk[a]}
		self.set_chkd_corfs(chkd_corfs)

	def _write_g1(self):
		head= "T={}, q={} \n".format(self.ave_Ts, self.ave_condis['q'])
		head+="t(s) \t g1(average) \n"
		np.savetxt("g1_T{}K_theta{}deg.out".format(int(self.ave_Ts), int(self.ave_condis['Theta'])), self.get_avg_nmz_corf(), header=head)

	def _write_msd(self):
		head= "T={}, q={} \n".format(self.ave_Ts, self.ave_condis['q'])
		head+="t(s) \t g0(average) \n"
		np.savetxt("g0_T{}K_theta{}deg.out".format(int(self.ave_Ts), int(self.ave_condis['Theta'])), self.get_msd(), header=head)
	
	def _write_G(self, R_H):
		head= "T={}, q={}, r={}".format(self.ave_Ts, self.ave_condis['q'], R_H)
		head+="s(s^(-1)) \t G_tilde (Pa) \t G' (Pa) \t G'' (Pa) \n"
		np.savetxt("G_T{}K_theta{}deg.out".format(int(self.ave_Ts), int(self.ave_condis['Theta'])), self.get_G(), header=head)	

	def _calc_initial_viscosity(self, R_H):
		q=self.ave_condis['q']
		T=self.ave_Ts
		meantau=np.average([self.get_fit_rsls()[a].params['beta'].value for a in self.get_fit_rsls()])**-1
		meanstretch=np.average([self.get_fit_rsls()[a].params['stretch'].value for a in self.get_fit_rsls()])
		tau=meantau/meanstretch*scipy.special.gamma(meanstretch**-1)
		rate=tau**-1
		self.initial_viscosity=q**2*k_B*T/(6*np.pi*rate*R_H)

########### PUBLIC VISUALIZATION METHODS
	def plot_nmz_g2min1(self):
		corfs=self.get_nmz_corfs()
		avg_nmz_corf=self.get_avg_nmz_corf()
		fig, ax = pp.subplots()
		coldct={a:Ttoclr(int(self.condis[a]['T']), 292.0, 320.0) for a in corfs}
		[ax.plot(corfs[a][:,0], corfs[a][:,1],  markersize=5, marker='o', mfc='None', mec=coldct[a], mew=1, lw=0, label=a[:-4]) for a in corfs]
		ax.plot(avg_nmz_corf[:,0], avg_nmz_corf[:,1], lw=2, color='black', label='Average')
		ax.loglog()
		fig.legend()
		ax.set_xlabel("t (s)")
		ax.set_ylabel("$g_2 - 1$")
		ax.set_ylim((4e-4,3))
		fig.savefig("nmzg2min1_T{}K_thea{}deg.pdf".format(int(self.ave_Ts), int(self.ave_condis['Theta'])))
		return fig, ax

	def plot_g2min1_fits(self):
		rsls=self.get_fit_rsls()
		corfs=self.get_sqrtg2min1()
		fig, ax = pp.subplots()
		for a in corfs:
			ax.plot(corfs[a][:,0], corfs[a][:,1],  markersize=5, marker='o', mfc='None', mec=clrs.next(), mew=1, lw=0, label=a[:-4])
			ax.plot(corfs[a][:,0], fn.stretchexp(rsls[a].params, corfs[a][:,0]), lw=1, markersize=0, c=clrs.current())
		ax.loglog()
		ax.set_xlabel("t (s)")
		ax.set_ylabel("$g_2 - 1$")
		fig.legend()
		ax.set_ylim((4e-4,3))
		fig.savefig("g2min1fit_T{}K_thea{}deg.pdf".format(int(self.ave_Ts), int(self.ave_condis['Theta'])))
		return fig, ax

############ PUBLIC ANALYSIS METHODS
	def avg_nmz_corfs(self, fit_uptocor=0.7):
		"""
		De facto factory method, currently needs to be called explicitly. The possible need for fitting parameters
		requires interaction with user directly, or through a Data class that is normally responsible for creating
		Analysis types.
		"""
		self._select_corfs()
		self._sqrt_corfs()
		self._fit_corfs_strexp(fit_uptocor)
		self._nmz_corfs()
		self.set_avg_nmz_corf(ave_dct_maxidx(self.get_nmz_corfs()))
		self._write_g1()

	def g2tsf(self, R_H):
		g1=self.get_avg_nmz_corf()
		T=self.ave_Ts
		q=self.ave_condis['q']

		self._calc_initial_viscosity(R_H)
		self.set_msd(g12msd(g1,q,T))
		self._write_msd()

		g0=self.get_msd()
		self.set_G(msd2G(g0, R_H, T, derfilter=sg.savgol_filter, derfilter_args=[31,3]))
		self._write_G(R_H)	
	
class CorData(at.Data):
	"""
	Class based on autotools.Data for reading out correlation functions, count rates, and measurement conditions
	from *.asc files.
	def __init__(self, path="", mask="*.asc", sortkey=lambda filename:filename):
	"""

	def _read_corfs(self):
		datas={name:openALV(name) for name in self.get_filelist()}
		raw_cor_dict={j:datas[j][ "\"Correlation\"" ] for j in datas}
		# average over the correlations obtained from the two detectors
		ave_detectors_cor={j:np.transpose(np.vstack([raw_cor_dict[j][:,0],\
				np.average(raw_cor_dict[j][:,[1,2]], axis=1)])) for j in raw_cor_dict}
		self.cor_dict=ave_detectors_cor
		# average over the count rates obtained from the two detectors
		rcsd={j:datas[j][ "\"Count Rate\"" ] for j in datas}
		ave_detectors_counts={j:np.transpose(np.vstack([rcsd[j][:,0],np.average(rcsd[j][:,[1,2]], axis=1)])) for j in rcsd}
		self.counts_series_dict=ave_detectors_counts
		self.condis_dict={j:read_conditions(j) for j in datas}

	def _ave_dict(self, dictionary, column_idx, key_to_int=lambda string: int(string[:-4])):
		"""
		Average the entire n-th column of value for every key, return a two-column numpy
		array with [int(key), average(nth column)]. Useful for extracting averages of
		count rates. Borrowed from lftools.screen_dir method.
		"""
		return {key:np.average([dictionary[key][:,column_idx]]) for key in dictionary}

	def _read_condition(self, dictionary, conditions=["T","Theta","eta","lambda0","q","r_idx"], key_to_int=lambda string: int(string[:-4])):
		self.condis=np.array([ np.hstack([ np.array([key_to_int(key)]), \
			np.array( [ dictionary[key][condition] for condition in conditions ]  )])  for key in dictionary ])
		self.condis=self.condis[ self.condis[:,0].argsort() ]

	def _read_count_rates(self):
		self.ave_counts_dict=self._ave_dict(self.counts_series_dict, 1)

	def _build_condis_vs_count_rates(self, dictionary, conditions=["T"], key_to_int=lambda string: int(string[:-4])):
		frame_T_count_rate=[]
		for key in dictionary:
			frame=key_to_int(key)
			# the variable is called T here, but it could be any condition (for example eta)
			T=np.array([dictionary[key][condition] for condition in conditions])
			count_rate=self.ave_counts_dict[key]
			frame_T_count_rate.append( np.hstack([np.array(frame), np.array(T), np.array(count_rate)]) )
		frame_T_count_rate=np.array(np.array(frame_T_count_rate))
		self.frame_T_count_rate=frame_T_count_rate[frame_T_count_rate[:,0].argsort()]

	def set_ranges(self, ranges):
		self.ranges=ranges

	def get_ranges(self):
		return self.ranges

	def set_analyses(self, analyses):
		self.analyses=analyses

	def get_analyses(self):
		return self.analyses

	def get_cordict(self):
		return self.cor_dict

	def get_counts_series_dict(self):
		return self.counts_series_dict

	def get_condis_dict(self):
		return self.condis_dict

	def get_ave_counts_dict(self):
		return self.ave_counts_dict

	def get_condis(self):
		return self.condis

	def get_frame_T_count_rate(self):
		return self.frame_T_count_rate

	def plot_analysis_plan(self, ranges=None):
		xdata=self.frame_T_count_rate[:,0]
		y1data=self.frame_T_count_rate[:,1]
		y2data=self.frame_T_count_rate[:,2]
		fig=pp.figure()
		ax1=fig.add_subplot(111)
		ax2=ax1.twinx()
		ax1.plot(xdata,y1data)
		ax2.plot(xdata,y2data)
		if ranges != None:
			[ax1.plot([i[0],i[1]],np.ones(2)*[np.average(y1data[i[0]:i[1]])], \
				marker='o', linestyle='-', linewidth=3) for i in ranges]
		pp.show()
		return fig, [ax1,ax2]


	def split_data(self, Nruns, lruns=[80], starts=[1], Nskips=[0],\
			binsize=5, threshold_frac=0.5, mean_tolerance_frac=0.1):
		"""
		Based on the input Nruns, runs, starts, packages the correlation functions into CorAnalysis
		objects. Nruns are ordered; length and starts need to be specified only for the first run.
		The rest will be autocompleted by using the last value. The actual analyses are performed
		by CorAnalysis objects that are created by the method and stored in the class.
		"""
		# TODO at the moment, this procedure is broken and unstraightforward to use
		# step one: correct input parameters
		print("split_data not recommended. Use auto_split_data if possible")
		if len(lruns) < Nruns: lruns+=[lruns[-1] for i in range (len(lruns)+1,Nruns+1) ]
		if len(Nskips) < Nruns: Nskips+=[Nskips[-1] for i in range (len(Nskips)+1, Nruns+1) ]
		if len(starts) < Nruns: starts+=[ starts[-1]+sum(lruns[:i-1]) for i in range(len(starts)+1, Nruns+1) ]
		print(lruns)
		print(starts)
		# step two: define ranges of frames to average
		ranges=[ (starts[i]+Nskips[i],starts[i]+lruns[i]) for i in range(0,len(starts)) ]
		self.set_ranges(ranges)
		self.create_analyses(binsize=binsize, threshold_frac=threshold_frac,\
				mean_tolerance_frac=mean_tolerance_frac)

	def find_T_jumps(self, min_runlength=5, Tthreshold=0.5, Tbinsize=5, safety_margin=5, skip_safety=[0,-1]):
		Tdiff=np.hstack([0,np.diff(self.get_frame_T_count_rate()[:,1])])
		Tdiff=smooth(Tdiff, Tbinsize)
		idcs_Tpeak=np.hstack([0,np.where(abs(Tdiff)>Tthreshold)[0]])
		print(idcs_Tpeak)
		diff_idcs_Tpeak=np.hstack([0, np.diff(idcs_Tpeak)])
		idcs_events=np.where(diff_idcs_Tpeak>min_runlength)[0]
		events=np.hstack([0,np.array([idcs_Tpeak[idc] for idc in idcs_events]),len(self.get_frame_T_count_rate())])
		print(events)
		ranges=[ (events[i-1], events[i]) for i in range(1,len(events)) ]

		if -1 in skip_safety: skip_safety.append(len(ranges)-1) # the -1 gets ignored
		ranges=[ (ranges[i][0],ranges[i][1]-safety_margin*(i not in skip_safety)) for i in range(0,len(ranges))]

		return ranges

	def prepare_cors(self, rng, f2file=lambda f: '{:08d}.asc'.format(f)):
		f0=int(rng[0])
		f1=int(rng[1])
		file_list=self.get_filelist()
		trimmed_filelist=[f2file(f) for f in range(f0,f1+1) if f2file(f) in file_list]
		return trimmed_filelist

	def auto_split_data(self, lruns=[40], min_runlength=5, Tthreshold=0.5, Tbinsize=5, safety_margin=5, \
			binsize=5, threshold_frac=0.5, mean_tolerance_frac=0.1, muRheo=True):
		"""
		Looks at the conditions/count rates for all the correlation functions, compares them with
		*criteria* and packages them into reprentative runs as CorAnalysis objects. Those are stored
		in self.cor_runs.
		"""
		ranges=self.find_T_jumps(min_runlength, Tthreshold, Tbinsize, safety_margin)
		if len(lruns)<len(ranges): lruns+=[lruns[-1] for i in range(len(lruns)+1, len(ranges)+1)]
		# fill up requirements for run length
		# code is a mayhem
		ranges=[ (int(ranges[i][1]-lruns[i]), int(ranges[i][1])) for i in range(0,len(ranges)) ]
		print(ranges)
		self.set_ranges(ranges)
		self._create_analyses(binsize=binsize, threshold_frac=threshold_frac,\
				mean_tolerance_frac=mean_tolerance_frac, muRheo=muRheo)

	def _create_analyses(self, binsize=5, threshold_frac=0.5, mean_tolerance_frac=0.1, muRheo=True):
		ranges=self.get_ranges()
		self.plot_analysis_plan(ranges)
		file_lists=[ self.prepare_cors(rng) for rng in ranges ]
		counts=[ { filename:self.get_counts_series_dict()[filename] for filename in file_list }\
				for file_list in file_lists ]
		# if there is only one range, this spells mayhem!!
		print([ (self.get_frame_T_count_rate()[ rng[0]-1:rng[1]-1,1]) for rng in ranges ])
		ave_Ts=[ np.average(self.get_frame_T_count_rate()[ rng[0]-1:rng[1]-1,1]) for rng in ranges ]
		condis=[ { filename:self.get_condis_dict()[filename] for filename in file_list } for file_list in file_lists ]
		corfs=[ { filename:self.get_cordict()[filename] for filename in file_list } for file_list in file_lists ]
		# refactoring flag - this should be solved in a more OOP way...
		if not muRheo: self.set_analyses([ CorAnalysis(file_lists[i], counts[i], ave_Ts[i], condis[i], corfs[i], ranges[i]) \
				for i in range(0, len(file_lists))])
		if muRheo: self.set_analyses([ CorAverager(file_lists[i], counts[i], ave_Ts[i], condis[i], corfs[i], ranges[i]) \
				for i in range(0, len(file_lists))])
		[analysis.check_count_rates(binsize, threshold_frac, mean_tolerance_frac) for analysis in self.get_analyses()]
		[analysis.check_cor_integral() for analysis in self.get_analyses()]
		[analysis.correct_s_to_ms() for analysis in self.get_analyses()]
		[analysis.ave_cors(analysis.get_check()) for analysis in self.get_analyses()]
	##
	def rncnt(self):
		[analysis.continfit() for analysis in self.get_analyses()]

	##
	def __init__(self, path="", mask="*.asc", sortkey=lambda filename:filename):
		super(CorData, self).__init__(path, mask)
		self.sortkey=sortkey
		self._read_corfs()
		self._read_count_rates()
		self._read_condition(self.condis_dict, conditions=["T", "Theta", "eta", "lambda0", "q", "r_idx"])
		self._build_condis_vs_count_rates(self.condis_dict, conditions=["T"])

class CorDataCal(CorData):
	def _cal_cnt_fctr(self, monfile, attcalfile):
		if monfile==None:
			print("This instance of CorDataCal was not supplied a monitor diode count. Count factors will be unity.")
			cnt_fctr={f:1 for f in self.file_list}
		else:
			mon=twocol2dct(monfile)
			mondct=mon2fctr(mon, attcalfile)
			cnt_fctr={f:100/mondct[f] for f in self.file_list}
		self.cnt_fctr=cnt_fctr

	# this is a cheeky override of CorData's _read_corfs, intended to incorporate the new attenuation factor
	def _read_corfs(self):
		datas={name:openALV(name) for name in self.get_filelist()}
		raw_cor_dict={j:datas[j][ "\"Correlation\"" ] for j in datas}
		# average over the correlations obtained from the two detectors
		ave_detectors_cor={j:np.transpose(np.vstack([raw_cor_dict[j][:,0],\
				np.average(raw_cor_dict[j][:,[1,2]], axis=1)])) for j in raw_cor_dict}
		self.cor_dict=ave_detectors_cor
		# average over the count rates obtained from the two detectors
		rcsd={j:datas[j][ "\"Count Rate\"" ] for j in datas}
		ave_detectors_counts={j:np.transpose(np.vstack([rcsd[j][:,0],np.average(rcsd[j][:,[1,2]], axis=1)*self.cnt_fctr[j]])) for j in rcsd}
		self.counts_series_dict=ave_detectors_counts
		self.condis_dict={j:read_conditions(j) for j in datas}

	def _edit_CRs_in_condis(self, condis_dict):
		for f in condis_dict:
			condis_dict[f]["MeanCR"]=condis_dict[f]["MeanCR"]*self.cnt_fctr[f]
			condis_dict[f]["MeanCR0"]=condis_dict[f]["MeanCR0"]*self.cnt_fctr[f]
			condis_dict[f]["MeanCR1"]=condis_dict[f]["MeanCR1"]*self.cnt_fctr[f]

	def __init__(self, path="", mask="*.asc", monmask="*.mon", \
		attcalfile="/Users/aljosha/stack/PCC-PhD/Data/DLS/ABADLS-attcal/averages.out", \
		sortkey=lambda filename:filename):
		"""
		Constructor method for CorDataCal, child of CorData, child of Data
		"""
		super(CorData, self).__init__(path, mask) # this calls the constructor of at.Data!
		mons=gl.glob(monmask)
		if len(mons)==0: monfile=None
		if len(mons)>0: monfile=mons[-1]
		self._cal_cnt_fctr(monfile, attcalfile)

		self._read_corfs()
		self._edit_CRs_in_condis(self.condis_dict)
		self._read_count_rates()
		self._read_condition(self.condis_dict, conditions=["T", "Theta", "eta", "lambda0", "q", "r_idx"])
		self._build_condis_vs_count_rates(self.condis_dict, conditions=["T"])

class CorDataSingleChannel(CorData):
	def _read_corfs(self):
		datas={name:openALV(name) for name in self.get_filelist()}
		self.cor_dict={j:datas[j][ "\"Correlation\"" ] for j in datas}
		# average over the count rates obtained from the two detectors
		self.counts_series_dict={j:datas[j][ "\"Count Rate\"" ] for j in datas}
		self.condis_dict={j:read_conditions(j) for j in datas}
#		if self.condis_dict.values()[0]['Mode']!='SINGLE AUTO CH0': print("Use CorDataCal type instead")

	def __init__(self, path="", mask="*.asc"):
		"""
		Constructor method for CorDataSingleChannel, child of CorData, child of Data
		"""
		super(CorData, self).__init__(path, mask) # call to constructor of at.Data, not CorData
		self._read_corfs()
		self._read_count_rates()
		self._read_condition(self.condis_dict, conditions=["T", "Theta", "eta", "lambda0", "q", "r_idx"])
		self._build_condis_vs_count_rates(self.condis_dict, conditions=["T"])




#class CorTransform(CorAnalysis):
#

def repeatlog(seq=[0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9], nul=1, eind=1e4):
	ndecs=int(np.log10(eind/nul))
	space=[]
	[[space.append(i*10**e) for i in seq] for e in range(int(np.log10(nul)), ndecs+1)]
	return space

def cleanser(series, tol=1e-6, ycol=1):
	"""
	Returns (x,y) array out of which the values that are too small are stripped.
	Only sensible for ncol=2 arrays.
	"""
	series=np.transpose([series[:,0], series[:,ycol]])
	return(series[np.where(series[:,1]>tol)])

def twocol2dct(filename):
	f=open(filename)
	lns=f.readlines()
	dct={rt.cleanstr(l.split(" ")[0]):float(rt.cleanstr(l.split(" ")[1])) for l in lns if "#" not in l}
	f.close()
	return(dct)

def mon2fctr(mon, attcal="/Users/aljosha/stack/PCC-PhD/Data/DLS/ABADLS-attcal/averages.out"):
	att=np.loadtxt(attcal, dtype="string")
	avatt=[a for a in att if "AVERAGE" in a]
	mon2att={float(a[6]):float(a[0].split("-")[-1][:-4].replace("o",".")) for a in avatt}
	mons=np.array(mon2att.keys())
	mondct={asc:mon2att[mons[np.argmin(abs(mons-mon[asc]))]] for asc in mon}
	return mondct

def g12msd(g1, q, T):
        msd=np.vstack([g1[:,0], -6/q**2.0*np.log(g1[:,1])]).transpose()
        msd=np.vstack([msd[:,0], msd[:,1]]).transpose()
        return msd

def chopx(data, lims):
        idcs=np.where(data[:,0]>lims[0])
        idcs2=np.where(data[:,0]<lims[1])
        idx=[i for i in idcs[0] if i in idcs2[0]]
        data=data[idx]
        return data

def chopy(data, lims):
        idcs=np.where(data[:,1]>lims[0])
        idcs2=np.where(data[:,1]<lims[1])
        idx=[i for i in idcs[0] if i in idcs2[0]]
        data=data[idx]
        return data

def numder2(msd):
        lnmsd=np.vstack([np.log(msd[:,0]), np.log(msd[:,1])]).transpose()
        msdder=np.vstack([lnmsd[:,0], np.zeros(len(lnmsd[:,0]))]).transpose()
        msdder[0]=[lnmsd[0,0], lnmsd[1,1]-lnmsd[0,1] ]
        for i in range(1,len(lnmsd[:,0])-1):
                dy=lnmsd[i+1,1]-lnmsd[i-1,1]
                dx=lnmsd[i+1,0]-lnmsd[i-1,0]
                msdder[i]=[lnmsd[i,0], dy/dx]
        msdder[-1]=[lnmsd[-1,0], lnmsd[-1,1]-lnmsd[-2,1] ]
	return msdder

def msd2G(msd, r, T, derfilter=lambda f: f, derfilter_args=[]):
        """
        Transforms msd into G_tilde, G' and G''. msd is a two-column np array with d ln(<r2>)/d ln(t),
        r is the probe radius in m. Returns a four-column np array with s in [:,0], G_tilde in [:,1],
        G' in [:,2] and G'' in [:,3].
        """
        lnmsd=np.vstack([np.log(msd[:,0]), np.log(msd[:,1])]).transpose()
        msdder=np.vstack([lnmsd[:,0], np.zeros(len(lnmsd[:,0]))]).transpose()
        msdder[0]=[lnmsd[0,0], lnmsd[1,1]-lnmsd[0,1] ]
        for i in range(1,len(lnmsd[:,0])-1):
                dy=lnmsd[i+1,1]-lnmsd[i-1,1]
                dx=lnmsd[i+1,0]-lnmsd[i-1,0]
                msdder[i]=[lnmsd[i,0], dy/dx]
        msdder[-1]=[lnmsd[-1,0], lnmsd[-1,1]-lnmsd[-2,1] ]
	msdder=np.vstack([msdder[:,0], derfilter(msdder[:,1], *derfilter_args)]).transpose()

        s=[1/t for t in msd[:,0]]
        Gtilde_s=np.vstack([s, np.zeros(len(msdder))]).transpose()
        Gstar=np.vstack([s, [1j for i in range(0,len(s))]]).transpose()
        for i in range(0, len(s)):
                Gtilde_s[i,1]=k_B*T/(np.pi*r*msd[i,1]*scipy.special.gamma(1+msdder[i,1]))
                Gstar[i,1]=k_B*T/(np.pi*r*msd[i,1]*scipy.special.gamma(1+msdder[i,1])*1j**(-msdder[i,1]))
        Gprime=np.vstack([Gstar.real[:,0], Gstar.real[:,1]]).transpose()
        Gdubbleprime=np.vstack([Gstar.real[:,0], Gstar.imag[:,1]]).transpose()
        return np.vstack([Gtilde_s[:,0], Gtilde_s[:,1], Gprime[:,1], Gdubbleprime[:,1]]).transpose()

def main(*args):
	print("lftools always ready for chaos")

