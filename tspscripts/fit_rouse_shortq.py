# -*- coding: utf-8 -*-
"""
Created on Wed May  6 15:00:47 2015

@author: aljosha

Fits the short-q solution of the Rouse prediction for the dynamic form factor,
which is defined by F(q,t)/F(q)=exp(-Dq^2t) by finding diffusion coefficient D
that minimizes the differences between given form factor and the one predicted
by the short-q approximation derived from the Rouse model. 

ff_fit_Rouse_small_q (time, ff, q, Dtest=0.2) takes a time series with the time as time, 
form factor as ff, the wave vector over which ff was analyzed as q and a guess for the
diffusion coefficient as D. It returns the optimal D for the given data set along with
a boolean succes.

The main script is a test function. The rest is commited to ~/Scripts/tools.py
"""
from scipy import optimize
from numpy import *
import matplotlib.pyplot

import tools



# first try
#def rouse_q_027 (p, ff, t):
#    # experimental time shift parameter is experimental
#    D=p[0]
#    fitfunc=exp(-(t)*D*0.27**2)
#    errfunc=ff-fitfunc
#    return errfunc
    
def generate_1p_expo (q):
    def ff_rouse_short_q (p, ff, t):
        D=p[0]
        fitfunc=exp(-t*D*q**2)
        errfunc=ff-fitfunc
        return errfunc
    return ff_rouse_short_q    
    
    
def ff_fit_Rouse_small_q (time, ff, q, Dtest=0.2):
    rouseff=generate_1p_expo(q)
    D,succes = optimize.leastsq(rouseff, [Dtest], args=(ff, time))
    return D, succes


# test function
path_lin="/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.27.dat"
path_log="/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.27_100.159.dat"
data_lin=array(tools.import_ts(path_lin)[0])
data_log=array(tools.import_ts(path_log)[0])
# data_lin_log=merge_lin_log(data_lin, data_log, merge_at=0.1, overlap=10)

ff=data_log[:,3]
time=data_log[:,0]
D, succes=ff_fit_Rouse_small_q (time,ff, 0.27)
print str(D)

mintime=time[1] #skip the zero
maxtime=time[-1]
print mintime
print maxtime
time_curve=logspace(log(mintime)/log(10), log(maxtime)/log(10), len(time)*30)

pyplot.figure()
pyplot.plot(data_log[::,0], data_log[::,3], 'x', label="T=1.00, q=0.27", ms=3)
pyplot.plot(time_curve, exp(-1*(time_curve)*D[0]*0.27**2), label="exp(-tDq^2), D="+str(round(D[0],6)), lw=2)
pyplot.xscale('log')
pyplot.ylim(-0.05,1.05)
pyplot.legend(loc=3)
pyplot.xlabel("t",size="large")
pyplot.ylabel("F(q,t)/F(q)",size="large")

#pp=matplotlib.backends.backend_pdf.PdfPages('/home/users/aljosha/DATA/ff01-2015.04.29/T1.00-isf-logscale/q0.27-fitted.pdf')
#pyplot.savefig(pp ,format="pdf")
#pp.close()

pyplot.show()