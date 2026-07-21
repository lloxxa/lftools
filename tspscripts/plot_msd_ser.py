# -*- coding: utf-8 -*-

# plot a series of msd. 
# TODO: refactor it into an actually useful tool.

import matplotlib.pyplot as pp
import numpy as np

class empty():
    def __getitem__(self, *args):
        return None

def plot_series(path_series, columns=[0,1], label_series=empty(), output_file=None):
    markers=['x','o','v','^','>','<','*']
    colors=['b','r','g','c','m','y','k']
    for i in range(0,len(path_series)):
        data=np.loadtxt(path_series[i])[:,np.array([columns[0],columns[1]])]
        pp.plot(data[:,0], data[:,1], marker=markers[i%len(markers)],\
            markerfacecolor='none',\
            markeredgecolor=colors[i%len(colors)],\
            label=label_series[i],
            color=colors[i%len(colors)])
        pp.legend()
        

msdT044=['/tmpmnt/home/titanic3/sfrey/LJ_192x64/system-G/NVT-system-G/T0.44/\
ana-trajectory/msdlog_GVT0.44_100-800.dat',\
'/tmpmnt/home/titanic3/sfrey/LJ_384x32/system-L/NVT-system-L/T0.44/\
ana-trajectory/msdlog_LVT0.44_100-400.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_768x16/system-M/NVT-system-M/T0.44/\
ana-trajectory/msdlog_MVT0.44_100-220.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_1536x8/system-N/NVT-system-N/T0.44/\
ana-trajectory/msdlog_NVT0.44_100-160.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_3072x4/system-O/NVT-system-O/T0.44/\
ana-trajectory/msdlog_OVT0.44_100-160.dat']
labelsT044=['N=64, i=192', 'N=32, i=384', 'N=16, i=768', 'N=8, i=1536',\
'N=4, i=3072']
pp.figure()
plot_series(msdT044, [0,4], label_series=labelsT044)
pp.xscale('log')
pp.yscale('log')
pp.legend(loc=2)
pp.title("T=0.44",size=20)
pp.xlabel("$t$", size=20)
pp.ylabel("$g_0(t)$", size=20)
#pp.savefig("/tmpmnt/home/users/aljosha/RESULTS/msd_alllengths_T0.44.pdf")

msdT050=['/tmpmnt/home/titanic3/sfrey/LJ_192x64/system-G/NVT-system-G/T0.50/\
ana-trajectory/msdlog_GVT0.50_100-500.dat',\
'/tmpmnt/home/titanic3/sfrey/LJ_384x32/system-L/NVT-system-L/T0.50/\
ana-trajectory/msdlog_LVT0.50_100-240.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_768x16/system-M/NVT-system-M/T0.50/\
ana-trajectory/msdlog_MVT0.50_100-200.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_1536x8/system-N/NVT-system-N/T0.50/\
ana-trajectory/msdlog_NVT0.50_100-200.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_3072x4/system-O/NVT-system-O/T0.50/\
ana-trajectory/msdlog_OVT0.50_100-150.dat']
labelsT050=['N=64, i=192', 'N=32, i=384', 'N=16, i=768', 'N=8, i=1536',\
'N=4, i=3072']
pp.figure()
plot_series(msdT050, [0,4], label_series=labelsT050)
pp.xscale('log')
pp.yscale('log')
pp.legend(loc=2)
pp.title("T=0.50",size=20)
pp.xlabel("$t$", size=20)
pp.ylabel("$g_0(t)$", size=20)
#pp.savefig("/tmpmnt/home/users/aljosha/RESULTS/msd_alllengths_T0.50.pdf")

msdT070=['/tmpmnt/home/titanic3/sfrey/LJ_192x64/system-G/NVT-system-G/T0.70/\
ana-trajectory/msdlog_GVT0.70_100-260.dat',\
'/tmpmnt/home/titanic3/sfrey/LJ_384x32/system-L/NVT-system-L/T0.70/\
ana-trajectory/msdlog_LVT0.70_100-129.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_768x16/system-M/NVT-system-M/T0.70/\
ana-trajectory/msdlog_MVT0.70_100-109.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_1536x8/system-N/NVT-system-N/T0.70/\
ana-trajectory/msdlog_NVT0.70_100-109.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_3072x4/system-O/NVT-system-O/T0.70/\
ana-trajectory/msdlog_OVT0.70_100-109.dat']
labelsT070=['N=64, i=192', 'N=32, i=384', 'N=16, i=768', 'N=8, i=1536',\
'N=4, i=3072']
pp.figure()
plot_series(msdT070, [0,4], label_series=labelsT070)
pp.xscale('log')
pp.yscale('log')
pp.legend(loc=2)
pp.title("T=0.70",size=20)
pp.xlabel("$t$", size=20)
pp.ylabel("$g_0(t)$", size=20)
#pp.savefig("/tmpmnt/home/users/aljosha/RESULTS/msd_alllengths_T0.70.pdf")

msdT100=['/tmpmnt/home/titanic3/sfrey/LJ_192x64/system-G/NVT-system-G/T1.00/\
ana-trajectory/msdlog_GVT1.00_100-129.dat',\
'/tmpmnt/home/titanic3/sfrey/LJ_384x32/system-L/NVT-system-L/T1.00/\
ana-trajectory/msdlog_LVT1.00_100-109.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_768x16/system-M/NVT-system-M/T1.00/\
ana-trajectory/msdlog_MVT1.00_100-109.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_1536x8/system-N/NVT-system-N/T1.00/\
ana-trajectory/msdlog_NVT1.00_100-109.dat',
'/tmpmnt/home/titanic3/sfrey/LJ_1536x8/system-N/NVT-system-N/T1.00/\
ana-trajectory/msdlog_NVT1.00_100-109.dat']
labelsT100=['N=64, i=192', 'N=32, i=384', 'N=16, i=768', 'N=8, i=1536',\
'N=4, i=3072']
pp.figure()
plot_series(msdT100, [0,4], label_series=labelsT100)
pp.xscale('log')
pp.yscale('log')
pp.legend(loc=2)
pp.title("T=1.00",size=20)
pp.xlabel("$t$", size=20)
pp.ylabel("$g_0(t)$", size=20)
#pp.savefig("/tmpmnt/home/users/aljosha/RESULTS/msd_alllengths_T1.00.pdf")