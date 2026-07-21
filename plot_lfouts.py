#!/anaconda/bin/python
import lftools as lf
import matplotlib.pyplot as pp
import plottools as pt
import tools as ts
import glob as gl
import numpy as np
import matplotlib.ticker as tc
import sys
import fileinput

### TODO: document the usage of this beast
### TODO: stop giving names like "plot_lfouts.py" to code that writes publishable figures....
###
def main(titlestring="", minT=293, maxT=323, **kwargs):
	midframe=500
	format_options={"axis_labelsize":18, "legend_fontsize":20, "ticklabelsize":18, "y_maxticks":4} 
	plotargs={'mew':1, 'mfc':"None", 'ms':10, 'lw':1}
	cmap=lf.cmapc2h
	Ttoclr=lambda T: cmap(int((T-minT)/(maxT-minT)*255))
	
	condis=["T=", "q=", "eta=", "r_idx=", "frame0=", "framei="]
	file_list=gl.glob('*.lf.out')
	
	# package all data
	heads=lf.get_heads(file_list)
	condisdict={file_name:lf.read_condis_header(heads[file_name], condis) for file_name in file_list}
	datasdict={file_name:np.loadtxt(file_name)[:,(1,4)] for file_name in file_list}
	labeldict={file_name:'$\mathrm{{T={:.1f}}}$'.format(condisdict[file_name]['T']-273) for file_name in file_list}
	colordict={file_name:Ttoclr(condisdict[file_name]['T']) for file_name in file_list}
	markerdict={}
	for file_name in file_list:
		if condisdict[file_name]['frame0']<midframe:markerdict[file_name]='P'
		else: markerdict[file_name]='o'
	
	# determine the order to plot (to have the proper legend) (at present, this is ugly)
	# here, we order by the first frame in the corf average
	order_to_key=np.array([ [condisdict[file_name]['frame0'], file_name] for file_name in file_list  ])
	order_to_key=order_to_key[order_to_key[:,0].astype(float).argsort()][:,1]

	fig=pp.figure()
	ax1=fig.add_subplot(1,1,1)
	lf.plot_series_from_dict_ocd(datasdict, labeldict, colordict, markerdict, \
			order_to_key=order_to_key, **plotargs)
	lf.labels("$\mathrm{{R}}_{{\mathrm{{H}}}} \mathrm{{(nm)}}$", "$\mathrm{{I (a.u.)}}$", \
			titlestring,\
			xlim=[1e0,1e3],ylim=[-0.1,3.0])
	
	# draw a colorbar instead of a legend (considering the sheer number of series)
	#ax2=fig.add_subplot(1,2,2)
	ax2=fig.add_axes((0.70,0.3,0.1,0.60))
	img=ax2.imshow([[minT-273,maxT-273]], cmap)
	ax2.set_visible(False)
	cb=fig.colorbar(img, fraction=0.4, shrink=0.7, pad=0.25, format="%0.1f")
	cb.ax.tick_params(labelsize=format_options['legend_fontsize'])
	lct=tc.LinearLocator(numticks=4)
	lct.tick_values(minT, maxT)
	cb.locator=lct
	cb.update_ticks()
	
	pt.format_plot(ax=ax1,draw_legend=False, **format_options)
	pp.savefig("ABADLS03-LF38-Tramp.pdf")
	
if __name__=="__main__":
	options={}
	for line in open(sys.argv[1]):
		words=line.split("==")
		options[words[0]]=words[1]
	if "title" in options:title=options["title"]
	if "minT" in options:options["minT"]=float(options["minT"])
	if "maxT" in options:options["maxT"]=float(options["maxT"])
	else: title=""
	main(**options)
