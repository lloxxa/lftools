import numpy as np

def monoexp(params, x, data=None):
    A=params['A'].value
    beta=params['beta'].value
    model=A*np.exp(-beta*x)
    if data is None: return model
    return model-data

def biexp(params, x, data):
    A=params['A'].value
    B=params['B'].value
    betaA=params['betaA'].value
    betaB=params['betaB'].value
    model=A*np.exp(-betaA*x)+B*np.exp(-betaB*x)
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


def triexp(params, x, data):
    A=params['A'].value
    B=params['B'].value
    C=params['C'].value
    betaA=params['betaA'].value
    betaB=params['betaB'].value
    betaC=params['betaC'].value
    model=A*np.exp(-betaA*x)+B*np.exp(-betaB*x)+C*np.exp(-betaC*x)
    return model-data

def bistretchexp(params, x, data):
    A=params['A'].value
    betaA=params['betaA'].value
    stretchA=params['stretchA'].value
    B=params['B'].value
    betaB=params['betaB'].value
    stretchB=params['stretchB'].value

    model=A*np.exp(-betaA*(x**stretchA))+B*np.exp(-betaB*(x**stretchB))
    return model - data

def tristretchexp(params, x, data=None):
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
    if data is None:return model
    return model - data

