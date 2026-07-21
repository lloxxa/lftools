# -*- coding: utf-8 -*-
"""
Created on Tue Jun  9 10:27:04 2015

@author: aljosha
"""
import numpy as np
import tools as ts
import matplotlib.pyplot as pp

def weed_out(data, dep_col=1, threshold=0.1, weed=100):
    if data.shape[1] < 2:
        print "Can't weed on a vector, empty array or non-numpy structure"
        return data
        
    split_at = ts.index_first(data[:,dep_col], threshold)
    N_fs = split_at # amount of samples in the full regime
    N_tw = len(data) - split_at # amount of samples to weed
    N_w =  int(np.floor(N_tw/weed)) # amount of weeded samples # int(floor) to cope with decimal weed input
    
    data_out=np.zeros((N_fs+N_w+1,data.shape[1]))    
    
    data_out[:N_fs]=data[:N_fs]
    data_out[N_fs:]=data[N_fs::weed]
    
    return data_out



series=np.array(ts.import_ts("/tmpmnt/home/titanic2/hmeyer/ljbb150/runlj256x768D068bb150dpd/sdync_q0.48bw0.01.D068-mcol")[0])
weeded=weed_out(series,dep_col=3, threshold=0.05, weed=50)
pp.plot(series[:,0],series[:,3],label="Natural")
pp.plot(weeded[:,0],weeded[:,3],label="Weeded",marker="x")
pp.legend()