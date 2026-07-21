# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 10:42:59 2015

@author: aljosha
"""

class TrajectoriesDummy(object):  
    """
    A class to run tests on Tool and its derivatives.		
    """
    #
    def get_nfiles(self):
        return 1
    #
    def get_filestring(self, file_idxs=None):
        return self.path
        #
    #
    def get_nframes(self):
        return self.nframes
    #
    def __repr__(self):
        return "TrajectoriesDummy for path %s, to simulate an actual collection of trajectories"%(self.path)
    #
    def __init__(self, path="/Users/aljosha/Documents/PCC-Stage/tsphome/T044-ana-isf-add/isf_q8_bw0.01_GVT0.44_195-199.dat", *args, **kwargs):     
        """
        Constructor. The *args are ignored, but in this way the class can be used as an easy substitute for running tests.
        """
        self.path=path
        self.polymer_length=64
        self.nframes=1000
        self.samples_bef_linstep=1
        self.sampling="lin"
        self.__repr__()
        print("Warning: using a TrajectoriesDummy object. If you intend to do \
something useful, you are doing it wrong")
        #
    #
#