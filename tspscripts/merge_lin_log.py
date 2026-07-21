# -*- coding: utf-8 -*-
"""
Created on Tue May  5 10:44:27 2015

@author: aljosha

merges time series on a linear and log time scale by combining and re-sorting 
the two datasets

merge_lin_log(lin_series, log_series, merge_at, overlap) returns merged_series

lin_series and log_series are Nxc numpy arrays to store the linear and logarithmically sampled time series, respectively. 
merge_at and overlap are numerals, use merge_at to supply a time point from which on the linear time will be taken,
use overlap to specify the fraction of logarithmic samples after merge_at that will overlap with the linear samples.
log_series will be put in front of lin_series, and it is assumed that log_series is the shorter of the two: 


"""


import numpy as np
import tools
import matplotlib.pyplot as pyplot

def index_nearest(array, value):
    idx = (np.abs(array-value)).argmin()
    return idx

def merge_lin_log(lin_series, log_series, merge_at=10, overlap=0):
    # find the point closest to merge_at    
    if len(lin_series)<overlap*len(log_series): print "Currently, this will not work. Expect random exceptions anytime soon."

    lin_merge_at=index_nearest(lin_series[:,0], merge_at)
    log_merge_at=index_nearest(log_series[:,0], merge_at)
    
    # the logarithmically sampled series are taken first, and determine the extent of overlap
    idx_last_log=int(np.floor((1+overlap)*log_merge_at))
    idx_first_lin=lin_merge_at

    # truncate the numpy arrays
    log_series=log_series[0:idx_last_log]
    lin_series=lin_series[idx_first_lin:len(lin_series)]
    
    # merge the time series, arranged by time (d'oh)    
    all_series=np.concatenate((log_series, lin_series), axis=0)
    all_series=all_series[np.argsort(all_series[:,0])]
    
    return all_series
    
## test run before commiting it it to tools.py

path_lin="/tmpmnt/home/users/aljosha/DATA/ff01-2015.04.29/T1.00-isf-linscale/isf_100.159q0.27.dat"
path_log="/tmpmnt/home/users/aljosha/DATA/ff01-2015.04.29/T1.00-isf-logscale/isf_100.q0.27.dat"
data_lin=np.array(tools.import_ts(path_lin)[0])
data_log=np.array(tools.import_ts(path_log)[0])

data_lin_log=merge_lin_log(data_lin, data_log, merge_at=0.1, overlap=10)

pyplot.figure()
pyplot.plot(data_lin_log[:,0], data_lin_log[:,3], 'x')
pyplot.xscale('log')
pyplot.ylim(-0.05,1.05)
pyplot.show()