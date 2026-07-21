#!//anaconda/bin/python
import lftools as lf, plottools as pt
import numpy as np, matplotlib.pyplot as pp
import os
import itertools as it

# "~/Dropbox/pcc-phd/Data/DLS/ABADLS03-LF38-292mg-mL-3000s-Tramp20-60-20/plot_ABADLS03.py"
# be careful with pasting the thing

plotoptions={'axis_labelsize':24, 'ticklabelsize':18, 'titlesize':14}
legoptions={'leg_pos':1, 'leg_fs':14, 'frameon':True, 'ncol':2}
dirname=os.getcwd().split('/')[-1] # might fail on windows :(

minT=18; maxT=62; Tbw=maxT-minT
clrs=lf.cmapc2h
clr=lambda a: clrs(int((a-minT)/Tbw*255))
sc2clr=lambda a, smin, bw :int((a-smin)/bw*255)

		
def main():
	rcgcm=pp.get_cmap('Set1')
	rcgcolors=lf.rcycle([rcgcm(i) for i in range(0,rcgcm.N)])
	rcgmrks=lf.rcycle((".","o","v","P","s","*","+","2","3","4","8","<","p","1","^","h","H",">","x","X","D","d","|","_"))

	ascfiles=lf.openseries()
	means=np.array([[int(name[-10:-4]), ascfiles[2][name]['MeanCR'], ascfiles[2][name]['T']-273] for name in ascfiles[0]])
	# computes the average count rate over the two detectors
	counts={name:np.array([ascfiles[1][name][:,0], np.average(ascfiles[1][name][:,1:3],1)]).transpose() for name in ascfiles[1]}
	corfs={name:np.vstack([ascfiles[0][name][:,0], np.average(ascfiles[0][name][:,1:3],1)]).transpose() for name in ascfiles[0]}
	condis=ascfiles[2]
	
	minT=min([ascfiles[2][name]['T'] for name in ascfiles[2]])
	maxT=max([ascfiles[2][name]['T'] for name in ascfiles[2]])
	print([minT,maxT])

	rcgcolors.reset(); rcgmrks.reset()
	f_vs_time_rcg, ax=plot_counts_vs_time_rcg(counts, condis, means,  minT, maxT, clrs=rcgcolors, mrks=rcgmrks)
	f_vs_time_rcg.savefig(dirname+'-f-vs-time-rcg.pdf')
	
	rcgcolors.reset(); rcgmrks.reset()
	corfs_vs_tau_rcg, ax=plot_corr_vs_tau_rcg(corfs, condis, means, minT, maxT, clrs=rcgcolors, mrks=rcgmrks)
	corfs_vs_tau_rcg.savefig(dirname+'-corfs-vs-tau-rcg.pdf')

def plot_corr_vs_tau_rcg(corfs, condis, means, minT, maxT, clrs=lf.clrs, mrks=lf.mrks, weed=10):
	fig, ax=pp.subplots()
	ax_opts={'lw':1, 'ms':10, 'mew':2, 'alpha':0.4 }
	legoptions={'leg_pos':'center left', 'leg_fs':10, 'frameon':True, 'ncol':1, 'bbox_to_anchor':(1,0.5)}
#	clrs=it.cycle('C'+ str(i) for i in range(0,10)) #these colors are not totally pretty

	Tbw=maxT-minT

	graphs=[ax.plot(corfs[filename][::weed,0], corfs[filename][::weed,1], label='{:d}'.format(int(filename[-10:-4])),\
		marker=mrks.next(), c=clrs.next(), **ax_opts  )\
		for filename in sorted(corfs.keys())]

	ax.set_ylim((-0.1,1.1))
	ax.set_xscale(('log'))
	pt.format_plot(**plotoptions)
	
	box=ax.get_position()
	pt.format_leg(ax, graphs=[i[0] for i in graphs], **legoptions)

	ax.set_position([box.x0, box.y0, box.width*.8, box.height])
	ax.set_xlabel("$\\tau$ (ms)", bbox=dict(facecolor='white', alpha=0.7, edgecolor='None'))
	ax.xaxis.set_label_coords(0.5,-0.02)
	ax.set_ylabel("g$_2$ ($\\tau$)", bbox=dict(facecolor='white', alpha=0.7, edgecolor='None'))
	ax.yaxis.set_label_coords(-.05,0.5)
	ax.set_title(dirname)
	pp.tight_layout(rect=[0,0,0.90,1])

	return fig, ax

def plot_counts_vs_time_rcg(counts, condis, means, minT, maxT, clrs=lf.clrs, mrks=lf.mrks):
	fig, ax=pp.subplots()
	ax_opts={'lw':1, 'ms':6, 'mew':2, 'alpha':0.4 }
	legoptions={'leg_pos':'center left', 'leg_fs':10, 'frameon':True, 'ncol':1, 'bbox_to_anchor':(1,0.5)}

	maxcnt=max(means[:,1]); mincnt=min(means[:,1]); avebw=maxcnt-mincnt
	graphs=[]

	for filename in sorted(counts.keys()):
		graphs+=ax.plot(counts[filename][:,0]/60,counts[filename][:,1], label='{:d}'.format(int(filename[-10:-4])), \
			c=clrs.next(), marker=mrks.next(), **ax_opts)

	ylims=ax.get_ylim(); ax.set_ylim((ylims[0],ylims[1]))
	pt.format_plot(**plotoptions)
	box=ax.get_position()
	pt.format_leg(ax, graphs=graphs, **legoptions)
	
	# sketchy sketchy. but it's kind of pretty.
	ax.set_position([box.x0, box.y0, box.width*.8, box.height])
	ax.set_xlabel("t (min)", bbox=dict(facecolor='white', alpha=0.7, edgecolor='None'))
	ax.xaxis.set_label_coords(0.5,-0.02)
	ax.set_ylabel("f (kHz)", bbox=dict(facecolor='white', alpha=0.7, edgecolor='None'))
	ax.yaxis.set_label_coords(-.05,0.5)
	ax.set_title(dirname)
	pp.tight_layout(rect=[0,0,0.90,1])

	return fig, ax

if __name__=="__main__":
	main()
