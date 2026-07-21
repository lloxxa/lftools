#!/Users/HPUSER27/anaconda3/python

from subprocess import Popen
p = Popen("activate.bat", cwd=r"C:\Users\HPUSER27\anaconda3\Scripts")
stdout, stderr = p.communicate()

import lxftools as lxf
import matplotlib.pyplot as pp
import pandas as pd

lxfi=lxf.LXFDataCal()
ana=lxfi.analyze_all()
ana.plot_corf()
pp.show()
