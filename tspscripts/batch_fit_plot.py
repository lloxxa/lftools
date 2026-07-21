# -*- coding: utf-8 -*-
"""
Created on Mon May 11 09:43:26 2015

@author: aljosha

Function batch_fit_plot

Takes linfiles and logfiles, a list of filenames for linear and logarithmic dynamic form factors, and qlist, 
which is a list of wave vectors at which the series were correlated. merges the time series using merge_lin_log 
(takes merge_at and overlap to customize the merging), fits a decay in one exponent to all merged trajectories 
using the late-time asymptote F(q,t)/F(q)=exp(-tDq^2), returns a 2D array diffco with diffco[:,0]=qlist and 
diffco[:,1]=D for every merged trajectories and plots all datasets with fitted decay.

TODO: allow to pass fit_func into the function to allow fitting of an arbitrary function to any data set
TODO: allow to pass plot_func into the function to allow plotting of the fit to the arbitrary function in fit_func
"""

import tools
import numpy as np
from matplotlib import pyplot
import matplotlib
import matplotlib.backends.backend_pdf

def plot_func(time, ff, D, q): 
     
    
    mintime=time[1] #skip the zero
    maxtime=time[-1]
    print mintime
    print maxtime
    time_curve=np.logspace(np.log(mintime)/np.log(10), np.log(maxtime)/np.log(10), len(time)*30)
    
    
    
    line, =pyplot.plot(time, ff, 'x', ms=2)
    color=line.get_color()
    pyplot.plot(time_curve, np.exp(-1*(time_curve)*D*q**2), lw=0.5, color=color, label="T=1.00, q="+str(q) + " D= " + str(round(D,6)))
    pyplot.ylim(0.000000001, 100)
    pyplot.xlim(0, 2e5)
    pyplot.yscale('log')
    

    pyplot.xlabel("t",size="large")
    pyplot.ylabel("F(q,t)/F(q)",size="large")
    
#    pp=matplotlib.backends.backend_pdf.PdfPages('/home/users/aljosha/DATA/ff01-2015.04.29/T1.00-isf-logscale/q0.27-fitted.pdf')
#    pyplot.savefig(pp ,format="pdf")
#    pp.close()
    


def batch_fit_plot(linfiles, logfiles, qlist, merge_at=10, overlap=0.1, fit_func=tools.ff_fit_Rouse_small_q, plot_func=plot_func):
    
    params=np.zeros((len(linfiles),2))    
    params[:,0]=qlist
                              
    for i in range(0,len(linfiles)):
       linseries=np.array(tools.import_ts(linfiles[i])[0])
       logseries=np.array(tools.import_ts(logfiles[i])[0])
       q=qlist[i]
       
       series=tools.merge_lin_log(linseries, logseries, merge_at, overlap)
       time=series[:,0]
       ff=series[:,3]
       
       """ TODO: generalize towards any fittable function """
       params[i,1]=fit_func(time, ff, q)[0]
       plot_func(time, ff, params[i,1], q)
      
    
    return params

#diffco=batch_fit_plot([
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.27.dat",
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.37.dat",
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.47.dat",
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.57.dat",
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.67.dat"
#    ],[
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.27_100.159.dat",
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.37_100.159.dat",
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.47_100.159.dat",
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.57_100.159.dat",
#    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.67_100.159.dat"
#    ], np.arange(0.27,0.77,0.1))
    
#pp=matplotlib.backends.backend_pdf.PdfPages('/home/users/aljosha/DATA/ff_q0.27..q0.67_Rouse_small_q_semilogx.pdf')
#pyplot.savefig(pp ,format="pdf")
#pp.close()