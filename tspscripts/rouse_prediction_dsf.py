# -*- coding: utf-8 -*-
"""
Created on Mon May 18 10:44:41 2015

@author: aljosha
"""
# TODO: make a dynamic algorithm instead of shitty recursive-like one

import numpy as np
import scipy.integrate as itg
import matplotlib.pyplot as pp
import tools
import scipy.special as spc

#def integrand_one(x, u):
#    return (np.cos(u*x)/x**2)*(1-np.exp(-x**2))
#
#def h_of_u(u):
#    ding=2/np.pi*itg.quad(integrand_one, 0, np.inf, args=u)[0]
#    # print "a u-value of " + str(u) + " gives integral" + str(ding)
#    return ding
#
#def h_of_u_analytical(u):
#    ding= 2/np.pi*(np.exp(-u**2/4)*np.sqrt(np.pi)+(np.pi/2*u)*(-1 + spc.erf(u/2)))
#    #print "a u-value of " + str(u) + " gives integral" + str(ding)
#    return ding


def integrand_two(u, x):
    uxdivsq=u*x**(-0.5)
    h_of_u_val=2/np.pi*(np.exp(-uxdivsq**2/4)*np.sqrt(np.pi)+(np.pi/2*uxdivsq)*(-1 + spc.erf(uxdivsq/2)))
    #h_of_u_val=h_of_u_analytical(uxdivsq)
    return np.exp(-u-x**0.5*h_of_u_val)

def f_of_x(x):
    ding=itg.quad(integrand_two, 0, np.inf, args=x)[0]
    fout=itg.quad(integrand_two, 0, np.inf, args=x)[1]
    # print "an x-value of " + str(x) + " gives f " + str(ding) + " with error " + str(fout)
    return ding

# Wittmer et al J Stat Phys 145 1017(2001)
#def linear_expansion(x):
#    return 1 - x + x**(1.5)*(4*np.sqrt(2)/(3*np.sqrt(np.pi)))

#pp.clf()
    
time=np.logspace(-4, 4, num=1000)
#time=np.arange(0,1,0.5)

values=np.zeros((len(time),2))

values[:,0] = time
values[:,1] = [ f_of_x(time[i]) for i in range(0,len(time)) ]
pp.plot(values[:,0], values[:,1], 'x')

#tools.write_ser("/tmpmnt/home/users/aljosha/RESULTS/formfactor_Rouse_scaling_function.dat", values, ["# time","f(x)"])

#pp.plot(time, integrand_one(time, 10))
#
#values=np.zeros((len(time),2))
#
#values[:,0] = time
#values[:,1] = [ h_of_u(time[i]) for i in range(0,len(time)) ]
# 
#pp.plot(values[:,0], values[:,1])
#
#
##pp.plot(time, h_of_u(time, 40))
#pp.ylim(-2,2)
#pp.show()