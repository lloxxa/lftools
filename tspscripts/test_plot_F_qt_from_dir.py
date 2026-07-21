# -*- coding: utf-8 -*-
"""
Created on Tue Aug 18 17:08:45 2015

@author: aljosha
"""
import matplotlib.pyplot as pp, tools as ts
# lj192x64T050
w=0.0020145
be=1.304
path="/tmpmnt/home/titanic3/aljosha/sfrey-192x64/T0.50/"
mask="autodsf_qlog_q*"
re_2fnd_q="q_[\\d.]*b"
qvals=[1.093, 1.64, 2.187, 3.28, 4.374, 6.014]
wd_thr=dict(zip(qvals,[0,0,0,0,0,0]))
wd=dict(zip(qvals,[1,1,1,1,1,1]))
ts.plot_F_qt_from_dir(path, mask, re_2fnd_q, qvals, w, be, wd_thr, wd)
#pp.yscale("log")
pp.xscale("log")
pp.xlim((4e-7,1e3))
pp.ylim((-0.03,1.03))
pp.legend(loc=3)