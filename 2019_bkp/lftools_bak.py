import numpy as np, matplotlib.pyplot as pp
import tools as ts
import autotools.autotools as at
import sys
import CONTINWrapper as cw
import pdb
import plottools as pt
import itertools as it
import glob as gl
import matplotlib.colors as cl

CONTINPATH="continPY"
mrks=it.cycle((".",",","o","v" ,"^","<",">","1","2","3","4","8","s","p","P","*","h","H","+","x","X","D","d","|","_"))
cmapc2h=cl.LinearSegmentedColormap.from_list("cold2hot", [(0,0,0.30),(0,0.5,1.0),(1,0.28,0),(1,0,0)])

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

def ave_cor(cordict, keys=[], denominator=1e3):
	# calculates the average over the len(keys) correlation functions in dict cordict
	alldata=[]
	if not keys:
		keys=[i for i in cordict]
	alldata=[cordict[i] for i in cordict]
	nrow,ncol=np.shape(alldata[0])
	ave=np.array([[sum(i[k,j] for i in alldata)/len(keys) for j in range(0,ncol) ] for k in range(0,nrow)])
	ave[:,0]=ave[:,0]/denominator
	return ave

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
			if len(condis)==5: break
		else:
			print("Could not find experimental conditions in the input! Expect the unexpected..")
	condis["q"]=4*np.pi*condis["r_idx"]*np.sin(np.pi*(condis["Theta"]/180.)/2.)/condis["lambda0"]
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
def plot_series_from_dict_ocd(datasdict, labeldict, colordict, markerdict, order_to_key=None, **kwargs):
        """
        OCD-proof version for the classic plot_series_from_dict. Supply markers, labels, colors,
        and, optionally, an order for all the series. One series per key/series pair.
        Future: modify plotting towards a true OO-style.
        """
	if order_to_key==None: order_to_key=[[key,key] for key in datasdict]
	skeys=[i[1] for i in order_to_key]
	for key in skeys:
		print key
		pp.plot(datasdict[key][:,0],datasdict[key][:,1], c=colordict[key],\
			marker=markerdict[key], label=labeldict[key], **kwargs)
##
def labels(xlabel=None, ylabel=None, title=None, fontsize=20, xlog=True, ylog=False, xlim=None, ylim=None):
	if xlog: pp.xscale('log')
	if ylog: pp.yscale('log')
	if title: pp.title(title, fontsize=fontsize, y=0.93)
	if xlabel: pp.xlabel(xlabel, fontsize=fontsize)
	if ylabel: pp.ylabel(ylabel, fontsize=fontsize)
	if xlim: pp.xlim(xlim[0],xlim[1])
	if ylim: pp.ylim(ylim[0],ylim[1])

def twinplot(xdata, y1data, y2data, xlabel="", y1label="", y2label=""):
	# TODO add labeling and formating support
	# maybe that'll mean writing formating functions that work purely on the axes/figures objects
	fig=pp.figure()
	ax1=fig.add_subplot(111)
	ax2=ax1.twinx()
	ax1.plot(xdata,y1data)
	ax2.plot(xdata,y2data)
	pp.show()
	return fig, [ax1,ax2]

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

	def averg_condis(self):
		condis=self.get_condis()
		check=self.get_check()
		keys=[ key for key in condis[condis.keys()[0]]]
		ave_condis={key:np.average( np.array([ condis[filename][key] for filename in condis if check[filename]==True ]) ) for key in keys }
		self.set_ave_condis(ave_condis)

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
				print "File {} exceeds mean counts tolerance and is disabled".format(filename)
				clrcode=128; marker='X'
			# check if there are spikes of more than threshold_frac
			elif True in (abs(counts[filename][:,1]-averuncnt)>averuncnt*threshold_frac):
				check[filename]=False
				print "File {} exceeds absolute count tolerance and is disabled".format(filename)
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

		return None 

	def ave_cors(self, check, denominator=1):
		file_list=self.get_file_list()
		corfs=self.get_corfs()
		alldata=[corfs[filename] for filename in file_list if check[filename]==True]
		# check if all corfs have the same amount of rows. Raise an exception if not.
		nrowsdict={filename:len(corfs[filename]) for filename in file_list if check[filename]==True}
		nrowslist=[nrowsdict[filename] for filename in nrowsdict]
		if np.size(np.unique(nrowslist))!=1:
			print "Correlation files in range {} have no unique sample count"
			print "It is probably advisable to remove the offending file. I'll raise an exception."
			print nrowsdict
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
		pp.plot(avecorf[:,0],avecorf[:,1], label="Average", lw=3)
		pp.legend()

	def __init__(self, file_list, counts, ave_Ts, condis, corfs, rng):
		self.set_file_list(file_list)
		self.set_counts(counts)
		self.set_ave_Ts(ave_Ts)
		self.set_condis(condis)
		self.set_corfs(corfs)
		self.set_rng(rng)

class CorData(at.Data):
	"""
	Class based on autotools.Data for reading out correlation functions, count rates, and measurement conditions
	from *.asc files.
	"""
	def _read_params(self):
		return param_dict
	
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
	##	
	def _ave_dict(self, dictionary, column_idx, key_to_int=lambda string: int(string[:-4])):
		"""
		Average the entire n-th column of value for every key, return a two-column numpy
		array with [int(key), average(nth column)]. Useful for extracting averages of
		count rates. Borrowed from lftools.screen_dir method.
		"""
		return {key:np.average([dictionary[key][:,column_idx]]) for key in dictionary}
	
	def _read_condition(self, dictionary, conditions=["T","Theta","eta","lambda0","q","r_idx"], key_to_int=lambda string: int(string[:-4])):
		self.condis=np.array([ np.hstack([ np.array([key_to_int(key)]), np.array( [ dictionary[key][condition] for condition in conditions ]  )])  for key in dictionary ])
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
		print "split_data not recommended. Use auto_split_data if possible"
		if len(lruns) < Nruns: lruns+=[lruns[-1] for i in range (len(lruns)+1,Nruns+1) ]
		if len(Nskips) < Nruns: Nskips+=[Nskips[-1] for i in range (len(Nskips)+1, Nruns+1) ]
		if len(starts) < Nruns: starts+=[ starts[-1]+sum(lruns[:i-1]) for i in range(len(starts)+1, Nruns+1) ]
		print lruns
		print starts
		# step two: define ranges of frames to average
		ranges=[ (starts[i]+Nskips[i],starts[i]+lruns[i]) for i in range(0,len(starts)) ]
		self.set_ranges(ranges)
		self.create_analyses(binsize=binsize, threshold_frac=threshold_frac,\
				mean_tolerance_frac=mean_tolerance_frac)

	def find_T_jumps(self, min_runlength=5, Tthreshold=0.5, Tbinsize=5, safety_margin=5, skip_safety=[0,-1]):
		Tdiff=np.hstack([0,np.diff(self.get_frame_T_count_rate()[:,1])])
		Tdiff=smooth(Tdiff, Tbinsize)
		idcs_Tpeak=np.hstack([0,np.where(abs(Tdiff)>Tthreshold)[0]])
		print idcs_Tpeak
		diff_idcs_Tpeak=np.hstack([0, np.diff(idcs_Tpeak)])
		idcs_events=np.where(diff_idcs_Tpeak>min_runlength)[0]
		events=np.hstack([0,np.array([idcs_Tpeak[idc] for idc in idcs_events]),len(self.get_frame_T_count_rate())])
		print events
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
			binsize=5, threshold_frac=0.5, mean_tolerance_frac=0.1):
		"""
		Looks at the conditions/count rates for all the correlation functions, compares them with 
		*criteria* and packages them into reprentative runs as CorAnalysis objects. Those are stored
		in self.cor_runs. 
		"""
		ranges=self.find_T_jumps(min_runlength, Tthreshold, Tbinsize, safety_margin)
		if len(lruns)<len(ranges): lruns+=[lruns[-1] for i in range(len(lruns)+1, len(ranges)+1)] 
		# fill up requirements for run length
		ranges=[ (ranges[i][1]-lruns[i], ranges[i][1]) for i in range(0,len(ranges)) ]
		self.set_ranges(ranges)
		self.create_analyses(binsize=binsize, threshold_frac=threshold_frac,\
				mean_tolerance_frac=mean_tolerance_frac)

	def create_analyses(self, binsize, threshold_frac, mean_tolerance_frac):
		ranges=self.get_ranges()
		self.plot_analysis_plan(ranges)
		file_lists=[ self.prepare_cors(rng) for rng in ranges ]
		counts=[ { filename:self.get_counts_series_dict()[filename] for filename in file_list }\
				for file_list in file_lists ]
		ave_Ts=[ np.average(self.get_frame_T_count_rate()[ rng[0]-1:rng[1]-1,1]) for rng in ranges ] 
		condis=[ { filename:self.get_condis_dict()[filename] for filename in file_list } for file_list in file_lists ]
		corfs=[ { filename:self.get_cordict()[filename] for filename in file_list } for file_list in file_lists ]

		self.set_analyses([ CorAnalysis(file_lists[i], counts[i], ave_Ts[i], condis[i], corfs[i], ranges[i]) \
				for i in range(0, len(file_lists))])
		[analysis.check_count_rates(binsize, threshold_frac, mean_tolerance_frac) for analysis in self.get_analyses()]
	##
	def analyze_subsets(self, runcnt=True):
		# package all the data
		# create the CorAnalysis objects
		[analysis.correct_s_to_ms() for analysis in self.get_analyses()]
		ave_cors=[analysis.ave_cors(analysis.get_check()) for analysis in self.get_analyses()]
		if runcnt==True: cntouts=[analysis.continfit() for analysis in self.get_analyses()]
		# run the CONTIN fit
		
	##	
	def __init__(self, path="", mask="*.asc", sortkey=lambda filename:filename):
		super(CorData, self).__init__(path, mask, sortkey=sortkey)
		self._read_corfs()
		self._read_count_rates()
		self._read_condition(self.condis_dict, conditions=["T", "Theta", "eta", "lambda0", "q", "r_idx"])
		self._build_condis_vs_count_rates(self.condis_dict, conditions=["T"])

# def main(*args):
#	if len(args) not 3:
#		print("Usage: rea")
#		sys.exit()
#	with open(args[1]) as f:
