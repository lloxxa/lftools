# -*- coding: utf-8 -*-
"""
Created on Tue Jul 28 17:45:20 2015

@author: Alexei Filippov

/tmpmnt/home/boreas/aljosha/Scripts/autotools.py

Tools that wrap around the TSP collection of (YASP) tools.
"""

import numpy as np
import tools as ts
import glob as gl
import subprocess as sp
import numpy as np
import re



class DsfJob(object):
    """
    Stores lists of paths and parameters to be passed to the children of
    Tool, tohandle automatization in a convenient way. Currently, it works
    only with DsfMqTool, because of its specific constructors. (needs to be
    generalized in the future).
    Constructor reads a file input_file with eight columns for full control 
    over the jobs. File format is as follows:
    <dir> <mask> <samp> <weed> <plng> <qlis> <dq> <max_mem> <opfx>
    <samp>: either "lin" or "log"
    <plng>: polymer length
    <qlis>: q-list, supplied as [value1, value2, value3, ..., valueN]
    <opfx>: path+prefix to which job-specific info will be appended
    to construct an filename for output storage
    """
    #
    def _list_of_strings_to_list_of_lists(self, list_of_strings):
        """
        The list of vectors to analyze is supplied as a string that must
        literally be interpreted as a list of floats. So, "[0.27,0.37,0.47]"
        is converted to [0.27,0.37,0.47] by _list_of_strings_to_list_of_lists.
        
        _list_of_strings_to_list_of_lists(list_of_strings) -> list of floats
        """
        list_of_lists=[ [] for i in range(0,len(list_of_strings))]
        for i in range(0, len(list_of_lists)):
            # print("Gonna work on list_if_strings[i]=%s"%(list_of_strings[i]))
            list_of_lists[i]=list_of_strings[i][1:-1].split(',')
            list_of_lists[i]=list(map(float, list_of_lists[i]))
        #
        return list_of_lists
    #
    def _read_weed(self, list_unsafe_weed):
        """
        Changes weed to None if it is 0, gives them back as an integer.
        """
        safe_weed=[ int for i in list_unsafe_weed ]
        for i in range(0, len(list_unsafe_weed)):
            if int(list_unsafe_weed[i])==0:
                safe_weed[i]=None
            else:
                safe_weed[i]=int(list_unsafe_weed[i])
            #
        #
        return safe_weed
    #
    def _read_instructions(self, input_file):
        instructions=np.loadtxt(input_file, dtype=str)
        if len(np.shape(instructions)) == 1:
            instructions=instructions.reshape((1, len(instructions)))        
        #
        diry_list=instructions[:,0].tolist() # list of strings
        mask_list=instructions[:,1].tolist() # list of strings
        samp_list=instructions[:,2].tolist() # list of strings
        weed_list=self._read_weed(instructions[:,3])
        plng_list=list(map(int, instructions[:,4].tolist())) # list of integers
        qlis_list=self._list_of_strings_to_list_of_lists(instructions[:,5]) 
        #                                                 list of lists
        dq_list=list(map(float, instructions[:,6].tolist())) # list of floats
        maxm_list=list(map(float, instructions[:,7].tolist())) # list of.. whatever
        opfx_list=instructions[:,8].tolist()            # list of strings
        #
        return diry_list, mask_list, samp_list, weed_list, plng_list, \
            qlis_list, dq_list, maxm_list, opfx_list
        #
    #
    def __init__(self, input_file, *args, **kwargs):
        if "DataClass" in kwargs:
            self.DataClass=kwargs["DataClass"]
        else:
            self.DataClass=Trajectories
        #
        self.args=args
        self.diry_list, self.mask_list, self.samp_list, self.weed_list,\
            self.plng_list, self.qlis_list, self.dq_list, self.maxm_list,\
            self.opfx_list = self._read_instructions(input_file)
        #        
    #
    def _iterate_q(self, Trjs, qlist, dq, weed, maxm, opfx):
        for i in range(0, len(qlist)):
            # TODO: Please make it safe for other chains than N=64!!
            mem_per_frameq=0.004
            otpf=''.join([opfx, "q_%.2fbw_%.3f.dat"%(qlist[i], dq)])
            print("Writing to %s"%(otpf))
            maxq=int(maxm/(mem_per_frameq*Trjs.get_nframes()))
            current_tool=DsfMqTool("strufa_dynmq2.exe", Trjs, otpf, qlist[i],\
                dq, maxq, weed)
            current_tool.call()
        #
    #
    def call(self):
        for i in range(0,len(self.diry_list)):
            Trjs=self.DataClass(self.diry_list[i], self.mask_list[i], \
                self.samp_list[i], polymer_length=self.plng_list[i])
            self._iterate_q(Trjs, self.qlis_list[i], self.dq_list[i], \
                self.weed_list[i], self.maxm_list[i], self.opfx_list[i])
            #
        #
    #
#
def join_savely(list_of_strings, joinstring=' '):
    """
    _join_savely(list_of_strings) joins a list of strings "savely", to ensure that a list
    with only a single string will not be treated as a list of characters (which str.join does),
    and to return an empty string instead of a None when the list given to it is empty.
    Use whenever a string is absolutely required, such as in command line call construction.
    """
    if len(list_of_strings)==1:
        return list_of_strings[0]
    #
    elif len(list_of_strings) > 1:
        return joinstring.join(list_of_strings)
    #
    else:
        return ""
    # could give unexpected results                
#
class Tool(object):
    """
    Tool object constructed by Tool(tool_path, data, output_file) and defines a manipulation
    of the data files that are stored in data by a tool referenced by tool_path, the output
    being requested to output_file. The intended usage is to inherit the class and overload
    the call() method with tool-specific code.
    """
    def call(self, file_idxs=None, *args):
        callstring="%s %s %s > %s"%(self.tool_path, join_savely(args), self.data.get_filestring(file_idxs), self.output_file)
        sp.call(callstring, shell=True)        
        print(callstring)
    #
    # TODO: def call_partial(self, *args): 
    # exhausts a generator supplied by Data, to call the tool repeatedly over the
    # sets of datafiles supplied by the generator, or modify get_filestring to show this behavior
    #
    def __init__(self, tool_path, data, output_file):
        self.tool_path=tool_path
        self.data=data
        self.output_file=output_file
    #
    def __repr__(self):
        return "Tool object to call to %s with object type %s to write to %s"%(self.tool_path, self.data, self.output_file)
    #
#
class DsfTool(Tool):
    """
    Class to call strufa_dyn to calculate structure correlation functions. Construct 
    with DsfTool(tool_path, Trjs, output_file, q, dq, weed=None). When supplying 
    logarithmically sampled data, weed must be a whole multiple of the linear spacing, 
    constructor will raise a ValueError. Trjs is an autotools.Trajectories object that 
    manages access to the trajectory files. The memory load of the process is determined
    by the amount of trajectories supplied by the Trjs object and the amount of vectors
    with q+-dq as found by the correlation software. 
    """
    def set_frames(self, frames):
        self.frames=int(frames)
    #
    def get_frames(self):
        return self.frames
    #
    def _calc_frames(self, arbitrary_number=100):
        frames=self.Trjs.get_nfiles()*self.Trjs.nframes/self.weed + arbitrary_number
        return frames
    #
    def __init__(self, tool_path, Trjs, output_file, q, dq, weed=None):
        Tool.__init__(self, tool_path, Trjs, output_file)
        self.Trjs=self.data # alias data object to emphasize the use of YAST trajectories
        self.q=q
        self.dq=dq
        #
        sampling_scale=Trjs.sampling
        #        
        # use the linear spacing if weed is not assigned. It is 1 for linear trajectories.
        if weed==None:
            self.weed=Trjs.samples_bef_linstep
        # check if weed is a weed/samples_bef_linstep is a whole number, to prevent
        # cutting throught logarithmic progressions. if is safe to execute for linear
        # Trjs as well, and will catch users trying to provide a decimal weed
        elif weed!=None:
            if not round(float(weed/Trjs.samples_bef_linstep),6).is_integer(): # danger?
                print(("Can not savely initiate DsfTool on a Trajectories object with\
                sampling_scale %s, linear spacing %f and requested weed %f. "\
                %(sampling_scale, Trjs.samples_bef_linstep, weed)))                
                raise ValueError
            else:
                print(("Initializing DsfTool object with\
                sampling_scale %s, linear spacing %f and requested weed %f. "\
                %(sampling_scale, Trjs.samples_bef_linstep, weed)))
                self.weed=weed
            #
        #
        self.set_frames(self._calc_frames())
          #
          #
    #
    def call(self, file_idxs=None, *args):
        """ 
        Uses parent's method call(), but inserts the strufa_dyn-specific arguments.
        """
        Tool.call(self, file_idxs, str(self.q), str(self.dq),\
        "-weed %s"%(str(self.weed)), "-n %s"%(str(self.Trjs.polymer_length)),\
        "-m %s"%(self.get_frames()), *args)
    #
#
class DsfMqTool(DsfTool):
    """
    Class to call strufa_dynmq2.exe for calculating structure correlation functions
    in a memory-respecting way. Construct with DsfMqTool(tool_path, Trjs, output_file,
    q, dq, maxq, weed=None). When supplying logarithmically sampled data, weed must
    be a whole multiple of the linear spacing, otherwise parent class DsfTool will
    raise a ValueError. maxq is the maximum amount of vectors over which the correlators
    are stored in memory, and determines the memory load of the process together
    with the amount of trajectories supplie by the Trjs object.
    """
    def set_maxq(self, maxq):
        self.maxq=maxq
    #
    def get_maxq(self):
        return self.maxq
    #
    def __init__(self, tool_path, Trjs, output_file, q, dq, maxq, weed=None):
        DsfTool.__init__(self, tool_path, Trjs, output_file, q, dq, weed)
        self.maxq=maxq
    #
    def call(self, file_idxs=None, *args):
        DsfTool.call(self, file_idxs, "-Maxq %i"%(self.maxq), *args)
    #
#    
class Data(object):  
    """
    Data object constructed by Data(path, mask), with path pointing to a directory
    containing files that would match mask. As an example, for linear trajectories, use mask
    mdGVT*.pos.trj. Note that the Trajectories object provides more trajectory=related
    possibilities.
     Will work even if there are no matches for path_mask.            
    """
    import tools as ts
    import glob as gl
    #
    def _findfiles(self, path, mask):
        file_list=gl.glob(path+mask)
        file_list.sort()
        return file_list            
    #
    def get_filelist(self):
        return self.file_list    
    #
    def get_nfiles(self):
        return len(self.file_list)
    #
    def get_filestring(self, file_idxs=None):
        """
        get_filestring(self, file_idxs=None) returns a string with all paths in list self.file_list,
        separated by a space, that are requested by the array file_idxs. If it is None, get_filestring
        will assess the list size and return all member paths. If it is set, get_filestring will 
        cycle through the indices, and return the corresponding strings for the indices that are in range.
        get_filestring raises an AttributeError when provided out-of-range indices.
        """
        if file_idxs==None: # file_idxs is unset, all paths can be joined into string
            return join_savely(self.file_list[:])
        #
        elif len(file_idxs) == 0:
            return []
        #
        else:    
            try:
                trj_filestring=[ 0 for i in file_idxs ]
            #
            except TypeError: 
                print("Trajectory files to join into string must be supplied as a list of integers")
                raise TypeError
            #
        for i in range(0,len(file_idxs)):
            if i < self.get_nfiles():                
                trj_filestring[i]=self.file_list[file_idxs[i]] # typical idiom for replacement by dict,
            #                                                                 but list is easier to rejoin afterwards
            else:
                print("Invalid request to Trajectories.get_filestring: trj_idx outside range of\
                available trajectories")
                raise AttributeError
            #
        #
        return join_savely(trj_filestring)
        #
    #
    def __init__(self, path, mask):
        self.file_list=self._findfiles(path, mask)
        self.path=path
        self.mask=mask
    #
    def __repr__(self):
        return "Data taken from path+mask %s%s"%(self.path, self.mask)
    #
# end class Data
        
class Trajectories(Data):
    """
    Trajectories object constructed by Trajectories(path, mask, sampling, timestep=0, polymer_length=1, **kwargs), 
    with path pointing to a directory containing files that would match mask. Sampling must be either "lin" or
    "log", otherwise the constructor with raise an AttributeError. Timestep is only important for "log" trajectories,
    and is used as a consistency check. Some methods will generate warnings when it is not set. Supported kwargs are
    out_data_path, which is set to "out_data" by default. As an example, for linear trajectories, use mask
    mdGVT*.pos.trj. 
    
   """
   # TODO: maybe think about support for lin/log mixed collections of trajectories, instead of assuming them all
   # to be of the same family. It could be costly, however, to do the out_data for every single one.
    def get_out_data_path(self):
        return self.out_data_path
    #
    def get_nframes(self):
        return self.nframes
    #
    def __init__(self, path, mask, sampling, timestep=0, polymer_length=1,**kwargs):     
        """
        Constructor.
        """
        if sampling in ["lin","log"]: self.sampling=sampling
        else: 
            print("sampling must be set to either linear ('lin') or logarithmic ('log')")
            raise AttributeError
        #
        Data.__init__(self, path, mask)
        self.polymer_length=polymer_length
        self.timestep=timestep
        #        
        if "out_data" in kwargs:
            self.out_data_path=kwargs['out_data']
        #
        else:
            self.out_data_path="out_data"
        #
        self.dictIdx2SamplingInfo=self.find_sampling([0])
        self.ts, self.base, self.samples_bef_incr, self.samples_bef_linstep, self.linstep=self.find_sampling([0])[0]
        self.nframes=self.find_nframes([0])[0]
    #        
    def __repr__(self):
        return "Trajectories taken from path+mask %s%s"%(self.path, self.mask)
    #
    def find_nframes(self, trj_idxs):
        """
        find_nframes(trj_idxs), trj_idxs a list of integers, returns a dict trj_idx -> nframes
        Calls to out_data by sending the string in self.out_data_path to the shell, along with the chainlength
        for each trajectory index supplied in the list trj_idxs.
        """
        try:
            trj_nframes=[ 0 for i in trj_idxs ]
        except TypeError: 
            print("Trajectory files to analyze for framecount must be supplied as a list of integers")
            raise TypeError
        #
        dictIdx2Nframes=dict(list(zip(trj_idxs, trj_nframes)))
        #
        for i in trj_idxs:
            if i < self.get_nfiles():                
                callstring="%s %s %s"%(self.out_data_path, self.polymer_length, self.file_list[i])
                print(("Calling %s"%(callstring)))
                #
                out_data_out=sp.check_output(callstring, shell=True)
                #
                n_string=re.search("#n: [\d]*,", out_data_out).group()
                n_frames=int(re.search("[\d]*,", n_string).group()[0:-1])
                dictIdx2Nframes[i]=n_frames
            else:
                print("Invalid request to Trajectories._find_nframes: trj_idx outside range of\
                available trajectories")
                raise AttributeError
            #
        #
        return dictIdx2Nframes
        #return out_data_out
    #
    def _check_trj_idxs(self, trj_idxs):
        for i in trj_idxs:
            if i < self.get_nfiles():
                pass
            else:
                print(("Requested trajectory %s does not exist, furthest available is %s"%(str(i), str(self.get_nfiles()))))
                raise AttributeError
    #
    def _calc_sampling_info_log(self, tser):
        # check if the given and found timestep is identical
        detected_ts=tser[2]-tser[1]
        if detected_ts==self.timestep:
            timestep=self.timestep
        else:
            print(("_calc_sampling_info_log WARNING: Detected (%s) and given (%s) timestep do not match. Please make sure that you requested\
            logtime analysis on a logarithmically sampled trajectory file. Continuing analysis with detected timestep..."\
            %(str(detected_ts), str(self.timestep))))
            timestep=detected_ts
            
        # find the amount of samples before the first increase in step size and the rate of increase in step size
        # this is under the (naive?) assumption that the first two steps are always equal to the time step
        jumpsize=timestep
        base=None
        jumpcount=None
        samples_bef_increment=None
        #
        for i in range(0,len(tser[0:-2])):
            realjump=tser[i+1]-tser[i]
            nextjump=tser[i+2]-tser[i+1]
            print(("(tser[i+1]-tser[i])/timestep=%f"%(realjump)))
            print(("(tser[i+2]-tser[i+1])/timestep=%f"%(nextjump)))
            
            if jumpcount!=None: jumpcount+=1            
            #
            if (realjump>jumpsize and jumpcount>0 and samples_bef_increment==None):
                samples_bef_increment=jumpcount
                print(("Samples before increasing step size: %i"%(samples_bef_increment)))
            #   
            if (realjump>jumpsize and abs(realjump-jumpsize)>0.00001): 
                if base==None: #base is yet undiscovered; we have traversed the first increase
                    base=realjump/jumpsize
                    print(("base equals %f"%(base)))
                
                jumpcount=1
                jumpsize=realjump
                print(("New jumpsize %f"%jumpsize))
            #
            if ((nextjump < realjump) and (abs(nextjump-realjump)>timestep)): # apparently, we have reached the linterval
                print(("Nextjump < realjump: %f < %f"%(nextjump,realjump)))
                samples_bef_linstep=i+1
                linstep=tser[i+1]-tser[0]
                
                print(("Samples before taking a linstep: %i"%(samples_bef_linstep)))
                print(("Linstep: %f"%(linstep)))
                break # everything that there is to know is now known
            #
        return [round(timestep,6), round(base,2), samples_bef_increment, samples_bef_linstep, linstep]
    #
    def find_sampling(self, trj_idxs):
        """
        find_sampling(trj_idxs), trj_idxs a list of integers, returns a dict trj_idx -> [trj_ts, trj_base, trj_samples_bef_incr,
        trj_samples_bef_linstep, trj_linstep ] ), for access to all sampling information.
        """
#        TODO: make the value in the dict a dict itself for more easy and intuitive access. Can be done in a loop (most likely).
#        TODO: actually, for added generality it might be interesting to return a table, not a dict, so that specific trj_idxs can be
#        found on basis of their sampling characteristics        
        #
        try:
            trj_ts = [ 0 for i in trj_idxs ]
            trj_base = [ 0 for i in trj_idxs ]
            trj_samples_bef_incr = [ 0 for i in trj_idxs ]
            trj_samples_bef_linstep = [ 0 for i in trj_idxs ]
            trj_linstep = [ 0 for i in trj_idxs ]
        except TypeError: 
            print("Trajectory files to analyze for framecount must be supplied as a list of integers")
            raise TypeError
        #
        sampling_info=list(zip(trj_ts, trj_base, trj_samples_bef_incr, trj_samples_bef_linstep, trj_linstep))
        dictIdx2SamplingInfo=dict(list(zip(trj_idxs, sampling_info)))
        #
        self._check_trj_idxs(trj_idxs)
        
        if self.sampling=="lin":
            for i in trj_idxs:          
                callstring="%s %s %s"%(self.out_data_path, self.polymer_length, self.file_list[i])
                print(("Calling %s"%(callstring)))
                #
                out_data_out=sp.check_output(callstring, shell=True)
                tser = ts.construct_ts(out_data_out)[:,0]
                #
                dictIdx2SamplingInfo[i]=[ self.timestep, 1, 1, 1, tser[1]-tser[0] ]
                
        elif self.sampling=="log":
            for i in trj_idxs:
                callstring="%s %s %s"%(self.out_data_path, self.polymer_length, self.file_list[i])
                print(("Calling %s"%(callstring)))
                #
                out_data_out=sp.check_output(callstring, shell=True)
                tser = ts.construct_ts(out_data_out)[:,0]
                #
                dictIdx2SamplingInfo[i]=self._calc_sampling_info_log(tser)                
                
        return dictIdx2SamplingInfo
    #
    def get_sampling(self):
            return self.sampling
    #
#
        

        
    
def analyze_rm(max_mem, trj_list, outfile, q, Nmon, Nchains, nframes, tool_name="strufa_dynmq2.exe", weed=1, dq=0.1):
    """
    analyze_RM: tool to wrap around analysis software while respecting memory (RM), useful
    for the big stuff such as strufa_dyn on 1000 trajectory files. Works for Nmon=64, unclear whether
    it is safe to use for other chain lengths.
    """
    
    Np=Nmon*Nchains
    mem_per_frameq=0.004 #MB
    maxq=int(max_mem/(mem_per_frameq*nframes))
    
    if np.size(trj_list) > 1:
        trj_string = np.array([ [i+' '] for i in trj_list]).tostring()[0:-1]
    else:
        trj_string=trj_list
    
    callstring="echo {"+str(Np)+",{1.."+str(Np)+"}} | nohup " + tool_name + " " + str(q) + " " + str(dq)\
        + " -n " + str(64) + " -m " + str(nframes) + " -skipfirst" + " -Maxq " + str(maxq) + " " + trj_string +\
        " > " + outfile  
    
    print("Calling " +  callstring)
    #result=sp.call(callstring, shell=True) #danger
    
#    if result>0:
#        print("Call function returned an error")
#        raise AttributeError
#    
        
    
def find_trj_files(path, filehook="mdGVT*.pos.*", regex_2find_idx="\.[\d]{3,4}\."):
    """ def find_isf_files(path) returns list qvals with all q-values and dict{qvals, filenames} dictQ2F that turns up
    a filename for each target q-value """
    files=gl.glob(path+filehook)
    files.sort() # trajectories must be supplied with continuity to compute correlation over real time
    #print files
    
    try:
        idx_file2=[  [int(re.search(regex_2find_idx, i).group()[1:-1]), i]  for i in files]
    except AttributeError:
        print("Caught an AttributeError: No files found in " + path + filehook + " that match regex " + regex_2find_idx + "!")
        return None        
    
    dictIDX2F = dict(idx_file2)
    trjnos=np.sort(np.array(idx_file2)[:,0])        
    trjfiles=np.sort(np.array(idx_file2)[:,1])
    
    return trjnos, trjfiles, dictIDX2F   
    
    


#def generate_analysis(callstring, max_mem, trj_list, outfile, q, Nmon, Nchains, nframes, weed=1, dq=0.1):
#    """
#    generate_analysis() accepts a callstring function that generates a tool-specific string to run a
#    specific analysis tool. generate_analysis() provides the basic mechanism for handling trajectory 
#    files and some very basic steps for calculation of the memory requirements.
#    """
#    
#    def bare_analysis(callstring, max_mem, trj_list, outfile, q, Nmon, Nchains, nframes, weed, dq):
#        Np=Nmon*Nchains
#        mem_per_frameq=0.004 #MB
#        maxq=int(max_mem/(mem_per_frameq*nframes))
#        
#        trj_string=' '.join(trj_list)
#        if np.size(trj_list) > 1:
#            trj_string = np.array([ [i+' '] for i in trj_list]).tostring()[0:-1]
#        else:
#            trj_string=trj_list
#        
#        print "Calling " +  callstring
#        status=sp.call(callstring, shell=True)
#        print status
#        
#    return bare_analysis(callstring, max_mem, trj_list, outfile, q, Nmon, Nchains, nframes, weed, dq)
#    
#    
#    
#@generate_analysis
#def call_strufa_dynmq2(maxq, tool_name="strufa_dynmq2.exe"):
#    pass


#callstring="echo {"+str(Np)+",{1.."+str(Np)+"}} | nohup " + tool_name + " " + str(q) + " " + str(dq)\
#        + " -n " + str(64) + " -m " + str(nframes) + " -skipfirst" + " -Maxq " + str(maxq) + " " + trj_string +\
#        " > " + outfile  
#
#def custom_analyze_rm(max_mem, trj_list, outfile, q, Nmon, Nchains, nframes, callstring_creater, weed=1, dq=0.1, *args):
#    """
#    analyze_RM: tool to wrap around analysis software while respecting memory (RM), useful
#    for the big stuff such as strufa_dyn on 1000 trajectory files. Works for Nmon=64, unclear whether
#    it is safe to use for other chain lengths.
#    """
#    
#    Np=Nmon*Nchains
#    mem_per_frameq=0.004 #MB
#    maxq=int(max_mem/(mem_per_frameq*nframes))
#    
#    if np.size(trj_list) > 1:
#        trj_string = np.array([ [i+' '] for i in trj_list]).tostring()[0:-1]
#    else:
#        trj_string=trj_list
#    
#    callstring_creater(Np, q, dq, nframes, *args)
#    
#    print "Calling " +  callstring
#    #result=sp.call(callstring, shell=True) #danger
#    
##    if result>0:
##        print("Call function returned an error")
##        raise AttributeError
