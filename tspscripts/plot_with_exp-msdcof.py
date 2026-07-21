# -*- coding: utf-8 -*-
"""
Created on Thu May 21 09:49:46 2015

@author: aljosha
"""
import tools
import matplotlib.pyplot as pyplot
import numpy as np
import batch_fit_plot

msd="/tmpmnt/home/titanic3/sfrey/LJ_192x64/system-G/NVT-system-G/T1.00/ana-trajectory/msdlog_GVT1.00_100-129.dat"

diffco=batch_fit_plot.batch_fit_plot([
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.27.dat",
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.37.dat",
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.47.dat",
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.57.dat",
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-linscale/isf_100.159_q0.67.dat"
    ],[
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.27_100.159.dat",
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.37_100.159.dat",
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.47_100.159.dat",
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.57_100.159.dat",
    "/tmpmnt/home/users/aljosha/DATA/T1.00-isf-logscale/log_q0.67_100.159.dat"
    ], np.arange(0.27,0.77,0.1))

data= np.array(tools.import_ts(msd)[0])

for i in [0.27, 0.37, 0.47, 0.57, 0.67]:
    pyplot.plot(data[:,0], np.exp(-(1.0/6.0)*data[:,5]*i**2), label="exp(-q^2*g_cof(t)/6")

batch_fit_plot


pyplot.legend()       
