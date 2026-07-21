#!//anaconda/bin/python
import lftools as lf, plottools as pt
import numpy as np, matplotlib.pyplot as pp
import os, sys
import argparse

# "~/Dropbox/pcc-phd/Data/DLS/ABADLS03-LF38-292mg-mL-3000s-Tramp20-60-20/plot_ABADLS03.py"
# be careful with pasting the thing

plotoptions={'axis_labelsize':24, 'ticklabelsize':18, 'titlesize':14}
legoptions={'leg_pos':1, 'leg_fs':14, 'frameon':True, 'ncol':2}
dirname=os.getcwd().split('/')[-1] # might fail on windows :(

minT=18; maxT=62; Tbw=maxT-minT
clrs=lf.cmapc2h
clr=lambda a: clrs(int((a-minT)/Tbw*255))

pp.ion()

def main(minT=0, maxT=80, minf=0, maxf=1000):
	ascfiles=lf.openseries()
	means=np.array([[int(name[:-4]), ascfiles[2][name]['MeanCR'], ascfiles[2][name]['T']-273] for name in ascfiles[0]])
	# computes the average count rate over the two detectors
	counts={name:np.array([ascfiles[1][name][:,0], np.average(ascfiles[1][name][:,1:3],1)]).transpose() for name in ascfiles[1]}
	corfs={name:np.vstack([ascfiles[0][name][:,0], np.average(ascfiles[0][name][:,1:3],1)]).transpose() for name in ascfiles[0]}
	condis=ascfiles[2]

	f_vs_T=plot_counts_vs_T(means, minT, maxT, minf, maxf)
	f_vs_T.savefig(dirname+'-f-vs-T.pdf')

	runs=plot_runs(means, minT, maxT, minf, maxf)
	runs.savefig(dirname+'-run.pdf')

	f_vs_time, check=plot_counts_vs_time(counts, means, condis)
	f_vs_time.savefig(dirname+'-f-vs-time.pdf')
	
	corfs_vs_tau=plot_corr_vs_tau(corfs, check, condis, means)
	corfs_vs_tau.savefig(dirname+'-corfs-vs-tau.pdf')

def plot_runs(means, minT, maxT ,minf, maxf):
	ax1_opts={'lw':0, 'marker':'o', 'ms':10,'mew':1, 'mfc':'none', 'mec':'c', 'label':'f (kHz)'}
	ax2_opts={'lw':0, 'marker':'x', 'ms':10,'mew':1, 'mfc':'none', 'mec':'r', 'label':'T ($^\circ$C)'}
	fig, graphs, axs=lf.twinplot(means[:,0], means[:,1], means[:,2], ax1_opts, ax2_opts, \
			xlabel="#$_\\mathrm{run}$", y1label="f (kHz)", y2label="T ($^\circ$C)", \
			title=dirname)
	axs[0].set_ylim((minf, maxf))
	axs[1].set_ylim((minT, maxT))
	[pt.format_ax(ax, fig, **plotoptions) for ax in axs]
	pt.format_leg(axs[0],graphs=graphs,**legoptions)
	pp.tight_layout()	
	return fig

def plot_counts_vs_T(means, minT, maxT ,minf, maxf):
	ax_opts={'lw':0, 'marker':'o', 'ms':10,'mew':1, 'mfc':'none', 'mec':'c', 'label':'f (kHz)'}
	fig, ax=pp.subplots()
	graphs=ax.plot(means[:,2], means[:,1], **ax_opts)
	ax.set_xlabel("T ($^\circ$C)")
	ax.set_ylabel("f (kHz)")
	ax.set_xlim((minT, maxT))
	ax.set_ylim((minf, maxf))
	ax.set_title(dirname)
	pt.format_plot(**plotoptions)
	pt.format_leg(ax, graphs=graphs, **legoptions)
	pp.tight_layout()
	return fig

def plot_counts_vs_time(counts, means, condis, mean_tolerance_frac=1, threshold_frac=2, save=True):
	fig, ax=pp.subplots()
	ax_opts={'lw':0, 'marker':'o', 'ms':3,'mew':1, 'mfc':'none', 'mec':'c', 'label':'f (kHz)'}
	legoptions={'leg_pos':'center left', 'leg_fs':10, 'frameon':True, 'ncol':1, 'bbox_to_anchor':(1,0.5)}
	maxcnt=max(means[:,1]); mincnt=min(means[:,1]); avebw=maxcnt-mincnt
	clrs=lf.cmapc2h
	check={}; graphs=[]

	averuncnt=np.average(means[:,1])
	pp.axhline(averuncnt*(1-threshold_frac), lw=1, ls='--', c=clrs(255))
	pp.axhline(averuncnt*(1+threshold_frac), lw=1, ls='--', c=clrs(255))

	for filename in sorted(counts.keys()):
		avecnt=condis[filename]['MeanCR']
		sizecode=(avecnt-mincnt)/avebw*6; marker='o'
		clrcode=(condis[filename]['T']-273-minT)/Tbw*255

		if abs(avecnt-averuncnt)>mean_tolerance_frac*averuncnt: 
			check[filename]=False
			print "File {} exceeds mean counts tolerance and should be omitted".format(filename)
			marker='X'
		# check if there are spikes of more than threshold_frac
		elif True in (abs(counts[filename][:,1]-averuncnt)>averuncnt*threshold_frac):
			check[filename]=False
			print "File {} exceeds absolute count tolerance and is disabled".format(filename)
			marker='x'
		else:
			check[filename]=True
		# end if
		graphs+=ax.plot(counts[filename][:,0]/60,counts[filename][:,1], label='{:d}'.format(int(filename[:-4])), \
			ms=ax_opts['ms']+sizecode, c=clrs(int(clrcode)), alpha=0.5, lw=0, mew=2, marker=marker)

	ylims=ax.get_ylim(); ax.set_ylim((0,ylims[1]))
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

	return fig, check


def plot_corr_vs_tau(corfs, check, condis, means, weed=10):
	fig, ax=pp.subplots()
	ax_opts={'lw':0, 'marker':'o', 'ms':4,'mew':1, 'mfc':'none', 'mec':'c', 'label':'f (kHz)'}
	legoptions={'leg_pos':'center left', 'leg_fs':10, 'frameon':True, 'ncol':1, 'bbox_to_anchor':(1,0.5)}
	mrks={True:'o', False:'x'}
	maxcnt=max(means[:,1]); mincnt=min(means[:,1]); avebw=maxcnt-mincnt
#	c2s=lambda cnt: (cnt-mincnt)/avebw*8
	c2s=lambda cnt: ax_opts['ms']

	graphs=[ax.plot(corfs[filename][::weed,0], corfs[filename][::weed,1], label='{:d}'.format(int(filename[:-4])),\
		marker=mrks[check[filename]], c=clr( condis[filename]['T']-273 ), alpha=0.5, lw=1, mew=2,\
		ms=c2s(condis[filename]['MeanCR'])+ax_opts['ms']  )\
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

	return fig

if __name__=="__main__":
	parser=argparse.ArgumentParser()
	parser.add_argument('--minT', type=int)
	parser.add_argument('--maxT', type=int)
	parser.add_argument('--minf', type=int)
	parser.add_argument('--maxf' ,type=int)
	opts=vars(parser.parse_args(sys.argv[1:]))
	kwargs={key:opts[key] for key in opts if opts[key]}
	print(kwargs)	

	main(**kwargs)

	raw_input('Press the any-key to continue')
