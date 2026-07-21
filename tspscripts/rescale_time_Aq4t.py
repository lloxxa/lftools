# -*- coding: utf-8 -*-
"""
Created on Tue May 12 15:09:10 2015

rescale_time_Aq4t.py

@author: aljosha

Rescales a time vector by multiplying it with Aq^4, A being given by pi/144*W*b^4, 
where W is a monomer mobility, b is a statistical segment length. For T=1.00, b=1.331,
w=0.10535

TODO: maybe implement look-up of the values from own analysis or Joerg's tables.
"""

import tools
from matplotlib import pyplot
import matplotlib.backends.backend_pdf
import numpy as np

def Rouse_approx_saddle_point(x):
    return (np.pi**3*x/4)**(0.25)*np.exp(-2*np.sqrt(x/np.pi))
    


def plot_rescaled(time, ff, q, plott): 
    line, =plott.plot(time, ff, 'x', label="T=1.00, q="+str(q), ms=1.5)
    color=line.get_color()
    

        
    
#    pyplot.plot(time_curve, np.exp(-1*(time_curve)*D*q**2), label="exp(-tDq^2), D="+str(round(D,6)), lw=1.5, color=color)
    pyplot.xscale('log')
    pyplot.ylim(-0.05,1.05)
    
    
    pyplot.xlabel("Aq^4t",size=20)
    pyplot.ylabel("F(q,t)/F(q)",size=22)
    
    return color
    
#    pp=matplotlib.backends.backend_pdf.PdfPages('/home/users/aljosha/DATA/ff01-2015.04.29/T1.00-isf-logscale/q0.27-fitted.pdf')
#    pyplot.savefig(pp ,format="pdf")
#    pp.close()

def batch_rescale_plot(linfiles, logfiles, qlist, W=0.10535, b=1.331, merge_at=0, overlap=0, rescale_func=tools.ff_fit_Rouse_small_q, plot_func=plot_rescaled, msdcomq=[]):
    
    fig=pyplot.figure(figsize=(10,7))
    plott = fig.add_subplot(111)    
    
    if msdcomq:
        msd="/tmpmnt/home/titanic3/sfrey/LJ_192x64/system-G/NVT-system-G/T1.00/ana-trajectory/msdlog_GVT1.00_100-129.dat"
        data=np.array(tools.import_ts(msd)[0])
    
    for i in range(0,len(linfiles)):
       linseries=np.array(tools.import_ts(linfiles[i])[0])
       logseries=np.array(tools.import_ts(logfiles[i])[0])
       q=qlist[i]
       
       series=tools.merge_lin_log(linseries, logseries, merge_at, overlap)
       time=series[:,0]
       ff=series[:,3]
       
       time_resc=rescale_time_Aq4t(time, q, W, b)
       """ TODO: generalize towards any fittable function """
       
       color=plot_rescaled(time_resc, ff, q, plott)
       print q
       if min(abs(msdcomq-q))<0.0001: #hacky substitute for if q in msdcomq, which often gives false   
           msd_time_resc=rescale_time_Aq4t(data[:,0], q, W, b)
           pyplot.plot(msd_time_resc, np.exp(-(1.0/6.0)*data[:,5]*q**2), label="exp(-"+str(q)+"^2*g3(t)/6)", color=color)
            
    
    time_economy=np.logspace(-4,2,100)    
    #pyplot.plot(time_economy, Rouse_approx_saddle_point(time_economy), '--', label="Rouse (SPA)", lw=1)
    pyplot.plot(time_economy, tools.large_angle_Rouse_scaling(time_economy), '--',  label="Rouse", lw=2)    
    
    
    pyplot.setp(plott.get_xticklabels(), fontsize=16)
    pyplot.setp(plott.get_yticklabels(), fontsize=16)
        
    pyplot.legend(loc=3)       
    
#    pp=matplotlib.backends.backend_pdf.PdfPages('/home/users/aljosha/DATA/ff_q0.67-1.07_rescaled_xlog_smaller.pdf')
#    pyplot.savefig(pp ,format="pdf")
#    pp.close()    
    
    

def rescale_time_Aq4t(time, q, W, b):
    return time*q**4*W*b**4*np.pi/144
#   return time*q**2*W*b**4*np.pi/144 for external length scales.

batch_rescale_plot([
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.27.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.37.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.47.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.57.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.67.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.77.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.87.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.97.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q1.07.dat"
],[
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.27_100.159.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.37_100.159.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.47_100.159.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.57_100.159.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.67_100.159.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.77_100.159.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.87_100.159.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.97_100.159.dat",
"/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q1.07_100.159.dat"
], np.arange(0.27,1.17,0.1), msdcomq=[0.27, 0.67])
    
