from __future__ import division
from scipy.special import gamma
import numpy as np
import mittag_leffler as ml

def monoexp(params, x, data=None):
    A=params['A'].value
    beta=params['beta'].value
    model=A*np.exp(-beta*x)
    if data is None: return model
    return model-data

def biexp(params, x, data=None, logrsd=False):
    A=params['A'].value
    B=params['B'].value
    betaA=params['betaA'].value
    betaB=params['betaB'].value
    model=A*np.exp(-betaA*x)+B*np.exp(-betaB*x)
    if data is None: return model
    if logrsd: return abs(np.log(model)) - abs(np.log(data))
    return model-data

def stretchexp(params, x, data=None):
    A=params['A'].value
    beta=params['beta'].value
    stretch=params['stretch'].value
    model=A*np.exp(-beta*(x**stretch))
    if data is None: return model
    return model - data


def monoplusstretch(params, x, data=None):
    A=params['A'].value
    betaA=params['betaA'].value
    B=params['B'].value
    betaB=params['betaB']
    stretchB=params['stretchB'].value
    model=A*np.exp(-betaA*x)+B*np.exp(-betaB*(x**stretchB))
    if data is None: return model
    return model-data

def monoplus2stretch(params, x, data=None):
    A=params['A'].value
    betaA=params['betaA'].value
    B=params['B'].value
    betaB=params['betaB']
    stretchB=params['stretchB'].value
    C=params['C'].value
    betaC=params['betaC']
    stretchC=params['stretchC'].value

    model=A*np.exp(-betaA*x)+B*np.exp(-betaB*(x**stretchB))+C*np.exp(-betaC*(x**stretchC))
    if data is None: return model
    return model-data

def triexp(params, x, data=None):
    A=params['A'].value
    B=params['B'].value
    C=params['C'].value
    betaA=params['betaA'].value
    betaB=params['betaB'].value
    betaC=params['betaC'].value

    model=A*np.exp(-betaA*x)+B*np.exp(-betaB*x)+C*np.exp(-betaC*x)
    if data is None: return model
    return model-data

def bistretchexp(params, x, data=None, logrsd=True):
    A=params['A'].value
    betaA=params['betaA'].value
    stretchA=params['stretchA'].value
    B=params['B'].value
    betaB=params['betaB'].value
    stretchB=params['stretchB'].value

    model=A*np.exp(-betaA*(x**stretchA))+B*np.exp(-betaB*(x**stretchB))
#    print([A,betaA,stretchA,B,betaB,stretchB])
    if data is None:return model
    if not logrsd: return model - data
    if logrsd: return abs(np.log(model)) - abs(np.log(data))

def dct_bistretchexp(fits, x):
    """ it's just for plotting, not fitting """
    A=fits["A"]
    betaA=fits["betaA"]
    stretchA=fits["stretchA"]
    B=fits["B"]
    betaB=fits["betaB"]
    stretchB=fits["stretchB"]
    return A*np.exp(-betaA*(x**stretchA))+B*np.exp(-betaB*(x**stretchB))

def tristretchexp(params, x, data=None, logrsd=False):
    A=params['A'].value
    betaA=params['betaA'].value
    stretchA=params['stretchA'].value
    B=params['B'].value
    betaB=params['betaB'].value
    stretchB=params['stretchB'].value
    C=params['C'].value
    betaC=params['betaC'].value
    stretchC=params['stretchC'].value

    model=A*np.exp(-betaA*(x**stretchA))+B*np.exp(-betaB*(x**stretchB))+C*np.exp(-betaC*(x**stretchC))
    if any(np.isnan(model)): print(model)
    if any(np.isnan(model)): print(params)
    if data is None:return model
    if not logrsd: return model - data
    if logrsd: return abs(np.log(model)) - abs(np.log(data))

def maxwell(params, x, data=None):
    """ data should be two-column, since both components are optimized simultaneously """
    G_c=params['G_c'].value
    tau_c=params['tau_c']
    mGstor=G_c*tau_c**2*x**2/(1+x**2*tau_c**2)
    mGloss=G_c*tau_c*x/(1+x**2*tau_c**2)
    if data is None: return (mGstor, mGloss)
    return sum((abs(data[:,0]-mGstor), abs(data[:,1]-mGloss)))

def bi_maxwell(params, x, data=None):
    """ data - two-column matrix """
    G_c1=params['G_c1'].value
    G_c2=params['G_c2'].value
    tau1=params['tau1'].value
    tau2=params['tau2'].value
    Gp=G_c1*tau1**2*x**2/(1+x**2*tau1**2) + G_c2*tau2**2*x**2/(1+x**2*tau2**2)
    Gpp=G_c1*tau1*x/(1+x**2*tau1**2) + G_c2*tau2*x/(1+x**2*tau2**2)
    if data is None: return (Gp, Gpp)
    return sum([abs(data[:,0]-Gp), abs(data[:,1]-Gpp)])

def fracMax_l(params,x, data=None):
    """ data should be two-column, since both components are optimized simultaneously """
    G_s=params['G_s'].value
    tau=params['tau']
    beta=params['beta']
    mGstor=np.real((G_s*((1j)*x*tau)**beta)/(1+((1j)*x*tau)**(beta-1)) )
    mGloss=np.imag((G_s*((1j)*x*tau)**beta)/(1+((1j)*x*tau)**(beta-1)) )
    if data is None: return (mGstor, mGloss)
    return sum(abs(np.log(data[:,0])-np.log(mGstor)), abs(np.log(data[:,1])-np.log(mGloss)))

def ffm(params, x, data=None, logrsd=True):
    """ 
    data should be two-column, since both components are optimized simultaneously
    first compenent: real part. second component: imaginary part. could obviously be
    done with np's complex number interface, yet this works... 
    """
    bV=params['bV'].value
    bG=params['bG'].value
    alpha=params['alpha'].value
    beta=params['beta'].value
    Gstar=((bV*(1j*x)**alpha)*(bG*(1j*x)**beta))/((bG*(1j*x)**alpha)+(bV*(1j*x)**beta))
    Gp=np.real(Gstar)
    Gpp=np.imag(Gstar)
    if data is None: return (Gp, Gpp)
    if logrsd: return sum([abs(np.log(data[:,0])-np.log(Gp)), abs(np.log(data[:,1])-np.log(Gpp))])
    return sum([abs(data[:,0]-Gp), abs(data[:,1]-Gpp)])


def biffm(params, x, data=None):
    """ 
    data should be two-column, since both components are optimized simultaneously
    first compenent: real part. second component: imaginary part. could obviously be
    done with np's complex number interface, yet this works... 
    """
    bV1=params['bV1'].value
    bG1=params['bG1'].value
    alpha1=params['alpha1'].value
    beta1=params['beta1'].value
    bV2=params['bV2'].value
    bG2=params['bG2'].value
    alpha2=params['alpha2'].value
    beta2=params['beta2'].value
    Gstar=bV1*(1j*x)**alpha1*bG1*(1j*x)**beta1/(bG1*(1j*x)**alpha1+bV1*(1j*x)**beta1)+\
            bV2*(1j*x)**alpha2*bG2*(1j*x)**beta2/(bG2*(1j*x)**alpha2+bV2*(1j*x)**beta2)
    Gp=np.real(Gstar)
    Gpp=np.imag(Gstar)
    if data is None: return (Gp, Gpp)
    return sum(abs(np.log(data[:,0])-np.log(Gp)), abs(np.log(data[:,1])-np.log(Gpp)))

def mxw_fml(params, x, data=None):
    """
    Maxwell element in parallel with a fractional Maxwell liquid element.
    Data is a two-column matrix with [:,0] th real part and [:,1] the imaginary part.
    """
    # Maxwell element
    Gc=params['Gc']
    tauc=params['tauc']
    # Fractional Maxwell liquid element
    Gfml=params['Gfml']
    taufml=params['taufml']
    beta=params['beta']
    Gstar=Gc*1j*x*tauc/(1+1j*x*tauc) + (Gfml*(1j*x*taufml)**beta)/(1+(1j*x*taufml)**(beta-1))
    Gp=np.real(Gstar)
    Gpp=np.imag(Gstar)
    if data is None: return(Gp, Gpp)
    return(sum(abs(np.log(data[:,0])-np.log(Gp)), abs(np.log(data[:,1])-np.log(Gpp))))


def G_ffm(params, x, data=None, verbose=False, logresiduals=False):
    bV=params['bV'].value
    bG=params['bG'].value
    alpha=params['alpha'].value
    beta=params['beta'].value
    a=alpha-beta
    b=1-beta
    z=(-bG/bV*x**(alpha-beta))
    E=ml.ml(z, a, b)
    G=bG*x**(-beta)*E
    if data is None: return G
    if verbose: print(sum(abs(data-G)))
    if not logresiduals: return abs(data - G)
    if logresiduals: return np.log(abs(data - G))

def G_ffm_2m(params, x, data=None, verbose=False, logresiduals=False):
    bV1=params['bV1'].value
    bG1=params['bG1'].value
    alpha1=params['alpha1'].value
    beta1=params['beta1'].value
    bV2=params['bV2'].value
    bG2=params['bG2'].value
    alpha2=params['alpha2'].value
    beta2=params['beta2'].value

    a1=alpha1-beta1
    b1=1-beta1
    z1=(-bG1/bV1*x**(alpha1-beta1))
    E=ml.ml(z1, a1, b1)
    G1=bG1*x**(-beta1)*E

    a2=alpha2-beta2
    b2=1-beta2
    z2=(-bG2/bV2*x**(alpha2-beta2))
    E2=ml.ml(z2, a2, b2)
    G2=bG2*x**(-beta2)*E2
    G=G1+G2

    if data is None: return G
    if verbose: print(sum(abs(data-G)))
    if not logresiduals: return abs(data - G)
    if logresiduals: return np.log(abs(data - G))
