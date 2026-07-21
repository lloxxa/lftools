import glob as gl
import numpy as np
import tools as ts

# filelist=gl.glob('/tmpmnt/home/titanic3/sfrey/LJ_192x64/system-G/NVT-system-G/T1.00/ana-strufa/dsf*.dat')
filelist=gl.glob('/home/users/aljosha/DATA/sfrey-64x192-NVT-G/T1.00/dsf*lin.dat')
datas=[ ts.fastts(f) for f in filelist ]
print datas

q_list=np.array([0.55,0.82])
S_q=np.array(ts.import_ts("/tmpmnt/home/titanic3/sfrey/LJ_192x64/system-G/NVT-system-G/T1.00/ana-trajectory/ana-ssf/mav-ssf_GVT1.00_ave-105-109.dat")[0])

out_datas=[ [] for f in filelist ]
S_0=0.0589258 # for T=1.00

for i in range(0,len(q_list)):
    # q=q_list[i]
    q=S_q[ts.index_nearest(S_q[:,0], q_list[i]), 0]
    F_q=S_q[ts.index_nearest(S_q[:,0], q_list[i]), 2]

    print F_q
    # CAREFUL HERE IT IS CRUCIAL TO MIND FROM WHICH COLUMN OF DATAS[i,:,COLUMN] ONE IS READING
    out_datas[i]=ts.rescale_S_qt_dRPA(datas[i][:,0], datas[i][:,2], F_q, S_0, q, 0.10535, 1.331) 
    # HAVE YOU ALREADY THOUGHT ABOUT THE COLUMN YOU ARE READING FROM?
    
    
    
    ts.write_ser("/home/users/aljosha/dangerous_output/dsf_q"+str(q)+"_dRPA_scaled_lin.dat",out_datas[i],["Aq^4t","S(q,t)*F(q)/S(0)^2_F_q="+str(F_q)])



