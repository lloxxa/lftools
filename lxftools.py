import tools as ts
import ctypes
import matplotlib.pyplot as pp
import lftools as lf
import autotools as at
import numpy as np 
import glob as gl
import pandas as pd
import tools as ts
import matplotlib.pyplot as pp
import numpy as np
import sys
import os
import re
import lmfit as lm
import fncs as fn
from matplotlib import colormaps
from matplotlib.ticker import AutoMinorLocator, MaxNLocator, LogLocator
from matplotlib.transforms import blended_transform_factory as btf
from matplotlib import rc

def vft_eta(T, A, B, T_0):
    ln_eta=A+B/(T-T_0)
    eta=np.e**ln_eta*1e-3
    return eta


def open_xl(path,tab):
    with open(path, 'rb') as f:
        xl=pd.read_excel(f,tab)
    return xl

def wtf():
    """
    Window to front
    Thanks to chatgpt for the ctypes handling
    """
    wdw=pp.get_current_fig_manager().window
    hwnd = int(wdw.winId())
    ctypes.windll.user32.ShowWindow(hwnd, 9)  # SW_RESTORE
    ctypes.windll.user32.SetForegroundWindow(hwnd)

def lxf_readmeta(lxfpath):
    metas={}
    with open(lxfpath) as f:
        for l in f:
            if l[0]=="#":
                if "#Temperature" in l:
                    s=l.split(" ")
                    print(s)
                    metas["T"]=s[1]

    return metas

def lxf_readshift(lxfpath):
    lines=[]
    with open(lxfpath) as f:
        swt=False
        for l in f:
            if "[step]" in l:
                swt=True
            if swt:
                lines.append(l)
    
    ls=lines[4:-1]
    cols=lines[2].split("\t")
    cols=[c.replace("\n","") for c in cols]
    
    ls=[[r.replace("\n", "") for r in l.split("\t") ] for l in ls]
    df=pd.DataFrame.from_records(ls, columns=cols)
    print(df)
    return df.astype(float)

def lxf_conditions(ascpath):
    condis = {}
    with open(ascpath, encoding="latin1") as f:
        for line in f:
            words = line.split()
            if words:
                if words[0] == "Temperature":
                    condis["T"] = float(words[-1])
#                elif words[0] == "Viscosity":
#                    condis["eta"] = float(words[-1])*1e-3
                elif words[0] == "Refractive":
                    condis["r_idx"] = float(words[-1])
                elif words[0] == "Angle":
                    condis["Theta"] = float(words[-1])
                elif words[0] == "Wavelength":
                    condis["lambda0"] = float(words[-1])*1e-9
                elif words[0] == "MeanCR0":
                    condis["MeanCR0"] = float(words[-1])
#                elif words[0] == "MeanCR1":
#                    condis["MeanCR1"] = float(words[-1])
#				elif words[0]=="Mode":condis["Mode"]=" ".join(words[2:])[1:-2]
            if len(condis) == 5:
                break
        else:
            print(
                "Could not find experimental conditions in the input! Expect the unexpected..")
    condis["q"] = 4*np.pi*condis["r_idx"] * \
        np.sin(np.pi*(condis["Theta"]/180.)/2.)/condis["lambda0"]
    condis["monitor"]=lf.get_monitor_diode_value(ascpath)
#    if "MeanCR1" in condis:
#        condis["MeanCR"] = np.average([condis["MeanCR0"], condis["MeanCR1"]])
    return condis

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
    def __init__(self, filelist='!glob', path='', mask='*.asc'):
        if filelist=="!glob": self.file_list=self._findfiles(path, mask)
        else:
           self.file_list=filelist
        self.path=path
        self.mask=mask
    #
    def __repr__(self):
        return "Data taken from path+mask %s%s"%(self.path, self.mask)
    #
# end class Data
        
       

class LXFData(Data):
    """
    Class based on autotools.Data for reading out correlation functions, count rates, and measurement conditions
    from *.asc files.
    def __init__(self, path="", mask="*.asc", sortkey=lambda filename:filename):
    """

    def _read_corfs(self):
        datas = {name: lf.openALV(name) for name in self.get_filelist()}
        raw_cor_dict = {j: datas[j]["\"Correlation\""] for j in datas}
        # average over the correlations obtained from the two detectors
        ave_detectors_cor = {j: np.transpose(np.vstack([raw_cor_dict[j][:, 0],
                                                        raw_cor_dict[j][:, 1]])) for j in raw_cor_dict}
        self.cor_dict = ave_detectors_cor
        # average over the count rates obtained from the two detectors
        rcsd = {j: datas[j]["\"Count Rate\""] for j in datas}
        ave_detectors_counts = {j: np.transpose(np.vstack(
            [rcsd[j][:, 0], rcsd[j][:, 1]])) for j in rcsd}
        self.counts_series_dict = ave_detectors_counts

    def _ave_dict(self, dictionary, column_idx, key_to_int=lambda string: int(string[-8:-4])):
        """
        Average the entire n-th column of value for every key, return a two-column numpy
        array with [int(key), average(nth column)]. Useful for extracting averages of
        count rates. Borrowed from lftools.screen_dir method.
        """
        return {key: np.average([dictionary[key][:, column_idx]]) for key in dictionary}

    def _read_condition(self, conditions=["T", "Theta", "lambda0", "q", "r_idx"], key_to_int=lambda string: int(string[-8:-4])):
        self.condis_dict = {j: lxf_conditions(j) for j in self.get_filelist()}
        dictionary=self.condis_dict
        self.condis = np.array([np.hstack([np.array([key_to_int(key)]),
                                           np.array([dictionary[key][condition] for condition in conditions])]) for key in dictionary])
        self.condis = self.condis[self.condis[:, 0].argsort()]

    def _read_count_rates(self):
        self.ave_counts_dict = self._ave_dict(self.counts_series_dict, 1)

    def _build_condis_vs_count_rates(self, dictionary, conditions=["T"], key_to_int=lambda string: int(string[-8:-4])):
        frame_T_count_rate = []
        for key in dictionary:
            frame = key_to_int(key)
            # the variable is called T here, but it could be any condition (for example eta)
            T = np.array([dictionary[key][condition]
                          for condition in conditions])
            count_rate = self.ave_counts_dict[key]
            frame_T_count_rate.append(
                np.hstack([np.array(frame), np.array(T), np.array(count_rate)]))
        frame_T_count_rate = np.array(np.array(frame_T_count_rate))
        self.frame_T_count_rate = frame_T_count_rate[frame_T_count_rate[:, 0].argsort(
        )]

    def set_ranges(self, ranges):
        self.ranges = ranges

    def get_ranges(self):
        return self.ranges

    def set_analyses(self, analyses):
        self.analyses = analyses

    def get_analyses(self):
        return self.analyses

    def get_cordict(self):
        return self.cor_dict

    def get_counts_series_dict(self):
        return self.counts_series_dict

    def get_condis_dict(self):
        return self.condis_dict

    def get_ave_counts_dict(self):
        return self.ave_counts_dict

    def get_condis(self):
        return self.condis

    def get_frame_T_count_rate(self):
        return self.frame_T_count_rate

    def plot_analysis_plan(self, ranges=None):
        xdata = self.frame_T_count_rate[:, 0]
        y1data = self.frame_T_count_rate[:, 1]
        y2data = self.frame_T_count_rate[:, 2]
        fig = pp.figure()
        ax1 = fig.add_subplot(111)
        ax2 = ax1.twinx()
        ax1.plot(xdata, y1data)
        ax2.plot(xdata, y2data)
        if ranges != None:
            [ax1.plot([i[0], i[1]], np.ones(2)*[np.average(y1data[i[0]:i[1]])],
                      marker='o', linestyle='-', linewidth=3) for i in ranges]
        pp.show()
        return fig, [ax1, ax2]

    def split_data(self, Nruns, lruns=[80], starts=[1], Nskips=[0],
                   binsize=5, threshold_frac=0.5, mean_tolerance_frac=0.1):
        """
        Based on the input Nruns, runs, starts, packages the correlation functions into CorAnalysis
        objects. Nruns are ordered; length and starts need to be specified only for the first run.
        The rest will be autocompleted by using the last value. The actual analyses are performed
        by CorAnalysis objects that are created by the method and stored in the class.
        """
        # TODO at the moment, this procedure is broken and unstraightforward to use
        # step one: correct input parameters
        print("split_data not recommended. Use auto_split_data if possible")
        if len(lruns) < Nruns:
            lruns += [lruns[-1] for i in range(len(lruns)+1, Nruns+1)]
        if len(Nskips) < Nruns:
            Nskips += [Nskips[-1] for i in range(len(Nskips)+1, Nruns+1)]
        if len(starts) < Nruns:
            starts += [starts[-1]+sum(lruns[:i-1])
                       for i in range(len(starts)+1, Nruns+1)]
        print(lruns)
        print(starts)
        # step two: define ranges of frames to average
        ranges = [(starts[i]+Nskips[i], starts[i]+lruns[i])
                  for i in range(0, len(starts))]
        self.set_ranges(ranges)
        self.create_analyses(binsize=binsize, threshold_frac=threshold_frac,
                             mean_tolerance_frac=mean_tolerance_frac)

    def find_T_jumps(self, min_runlength=5, Tthreshold=0.5, Tbinsize=5, safety_margin=5, skip_safety=[0, -1]):
        Tdiff = np.hstack([0, np.diff(self.get_frame_T_count_rate()[:, 1])])
        Tdiff = lf.smooth(Tdiff, Tbinsize)
        idcs_Tpeak = np.hstack([0, np.where(abs(Tdiff) > Tthreshold)[0]])
        print(idcs_Tpeak)
        diff_idcs_Tpeak = np.hstack([0, np.diff(idcs_Tpeak)])
        idcs_events = np.where(diff_idcs_Tpeak > min_runlength)[0]
        events = np.hstack([0, np.array([idcs_Tpeak[idc] for idc in idcs_events]), len(
            self.get_frame_T_count_rate())])
        print(events)
        ranges = [(events[i-1], events[i]) for i in range(1, len(events))]

        if -1 in skip_safety:
            skip_safety.append(len(ranges)-1)  # the -1 gets ignored
        ranges = [(ranges[i][0], ranges[i][1]-safety_margin *
                   (i not in skip_safety)) for i in range(0, len(ranges))]

        return ranges

    def prepare_cors(self, rng, f2file=lambda f: '{:08d}.asc'.format(f)):
        f0 = int(rng[0])
        f1 = int(rng[1])
        file_list = self.get_filelist()
        trimmed_filelist = [f2file(f) for f in range(
            f0, f1+1) if f2file(f) in file_list]
        return trimmed_filelist

    def auto_split_data(self, lruns=[40], min_runlength=5, Tthreshold=0.5, Tbinsize=5, safety_margin=5,
                        binsize=5, threshold_frac=0.5, mean_tolerance_frac=0.1, muRheo=True):
        """
        Looks at the conditions/count rates for all the correlation functions, compares them with
        *criteria* and packages them into reprentative runs as CorAnalysis objects. Those are stored
        in self.cor_runs.
        """
        ranges = self.find_T_jumps(
            min_runlength, Tthreshold, Tbinsize, safety_margin)
        if len(lruns) < len(ranges):
            lruns += [lruns[-1] for i in range(len(lruns)+1, len(ranges)+1)]
        # fill up requirements for run length
        # code is a mayhem
        ranges = [(int(ranges[i][1]-lruns[i]), int(ranges[i][1]))
                  for i in range(0, len(ranges))]
        print(ranges)
        self.set_ranges(ranges)
        self._create_analyses(binsize=binsize, threshold_frac=threshold_frac,
                              mean_tolerance_frac=mean_tolerance_frac, muRheo=muRheo)

    def analyze_all(self, filelist=None, binsize=5, threshold_frac=3, mean_tolerance_frac=2, bypass_corint=False):
        """
        -> CorAverager
        Packages all files in the file_list into an CorAverager object.
        """
        if not filelist:
            filelist = self.get_filelist()
        ave_Ts = np.average(self.get_frame_T_count_rate()[:, 1])
        ana = lf.CorAverager(filelist, self.get_counts_series_dict(
        ), ave_Ts, self.get_condis_dict(), self.get_cordict(), [0, len(filelist)])
        # move to CorAverager constructor?
        ana.check_count_rates(binsize, threshold_frac, mean_tolerance_frac)
        if not bypass_corint: ana.check_cor_integral()
        ana.correct_s_to_ms()
        ana.ave_cors(ana.get_check())
        return ana

    def _create_analyses(self, binsize=5, threshold_frac=0.5, mean_tolerance_frac=0.1, muRheo=True):
        ranges = self.get_ranges()
        self.plot_analysis_plan(ranges)
        file_lists = [self.prepare_cors(rng) for rng in ranges]
        counts = [{filename: self.get_counts_series_dict()[filename] for filename in file_list}
                  for file_list in file_lists]
        ave_Ts = [np.average(self.get_frame_T_count_rate()[
                             rng[0]:rng[1], 1]) for rng in ranges]
        condis = [{filename: self.get_condis_dict()[filename]
                   for filename in file_list} for file_list in file_lists]
        corfs = [{filename: self.get_cordict()[filename]
                  for filename in file_list} for file_list in file_lists]
        if not muRheo:
            self.set_analyses([lf.CorAnalysis(file_lists[i], counts[i], ave_Ts[i], condis[i], corfs[i], ranges[i])
                               for i in range(0, len(file_lists))])
        if muRheo:
            self.set_analyses([lf.CorAverager(file_lists[i], counts[i], ave_Ts[i], condis[i], corfs[i], ranges[i])
                               for i in range(0, len(file_lists))])
        [analysis.check_count_rates(
            binsize, threshold_frac, mean_tolerance_frac) for analysis in self.get_analyses()]
        [analysis.check_cor_integral() for analysis in self.get_analyses()]
        [analysis.correct_s_to_ms() for analysis in self.get_analyses()]
        [analysis.ave_cors(analysis.get_check())
         for analysis in self.get_analyses()]
    ##

    def rncnt(self):
        [analysis.continfit() for analysis in self.get_analyses()]

    ##
    def __init__(self, filelist='!glob', path='', mask='*.asc', sortkey=lambda filename: filename):
        print("reporting from CorData constructor")
        super(LXFData, self).__init__(filelist, path, mask)
        self.sortkey = sortkey
        self._read_condition( conditions=[
                             "T", "Theta", "lambda0", "q", "r_idx"])

        self._read_corfs()
        self._read_count_rates()
        self._build_condis_vs_count_rates(self.condis_dict, conditions=["T"])

def mon2fctr(mon, attcal="C:\\Users\\HPUSER27\\Documents\\ICS-PostDoc\\DLS\\LXFDLS02_ATTCAL_PS300_H2O\\LXFDLS02_ATTCAL_PS300_H2O.out"):
    att = pd.read_csv(attcal, sep='\t')[1:] # we skip the dark current to avoid zeroes
    mondct = {asc: float(att.iloc[(att['monitor']-mon[asc]).abs().argsort()[:1]]['attenuation']) for asc in mon}
    return mondct


class LXFDataCal(LXFData):
    def _cal_cnt_fctr(self, attcalfile):
        mon = {f:self.condis_dict[f]['monitor'] for f in self.file_list}
        mondct = mon2fctr(mon, attcalfile)
        print(mondct)
        cnt_fctr = {f: 100/mondct[f] for f in self.file_list}
        self.cnt_fctr = cnt_fctr

    # this is a cheeky override of CorData's _read_corfs, intended to incorporate the new attenuation factor
    def _read_corfs(self):
        datas = {name: lf.openALV(name) for name in self.get_filelist()}
        print( datas )
        raw_cor_dict = {j: datas[j]["\"Correlation\""] for j in datas}
        # averageing disabled because now working mostly with one correlator... 
        ave_detectors_cor = {j: np.transpose(np.array([raw_cor_dict[j][:, 0],
                                                        raw_cor_dict[j][:, 1]])) for j in raw_cor_dict}
        self.cor_dict = ave_detectors_cor
        # average over the count rates obtained from the two detectors
        rcsd = {j: datas[j]["\"Count Rate\""] for j in datas}
        print(rcsd)
        ave_detectors_counts = {j: np.transpose(np.array([ rcsd[j][:, 0], rcsd[j][:, 1] ])) for j in rcsd}
        self.counts_series_dict = ave_detectors_counts
        self.condis_dict = {j: lxf_conditions(j) for j in datas}

    def _edit_CRs_in_condis(self, condis_dict):
        for f in condis_dict:
#            condis_dict[f]["MeanCR"] = condis_dict[f]["MeanCR"] * \
#                self.cnt_fctr[f]
            condis_dict[f]["MeanCR0"] = condis_dict[f]["MeanCR0"] * \
                self.cnt_fctr[f]
            condis_dict[f]["attcorfac"] = self.cnt_fctr[f]
            condis_dict[f]["attenuation"] = 100/self.cnt_fctr[f]
#            condis_dict[f]["MeanCR1"] = condis_dict[f]["MeanCR1"] * \
#                self.cnt_fctr[f]

    def __init__(self, filelist='!glob', path='', mask='*.ASC', 
                 attcalfile="C:\\Users\\HPUSER27\\Documents\\ICS-PostDoc\\DLS\\LXFDLS02_ATTCAL_PS300_H2O\\LXFDLS02_ATTCAL_PS300_H2O.out",
                 sortkey=lambda filename: filename):
        """
        Constructor method for CorDataCal, child of CorData, child of Data
        """
        super(LXFData, self).__init__(
            filelist, path, mask) # calls to autotools.Data.__init__()

        self._read_condition(conditions=[
                             "T", "Theta",  "lambda0", "q", "r_idx"])
        self._cal_cnt_fctr(attcalfile)
        self._read_corfs()
        self._read_count_rates()
        self._edit_CRs_in_condis(self.condis_dict)
        self._build_condis_vs_count_rates(self.condis_dict, conditions=["T"])


class LXFDataSingleChannel(LXFData):
    def _read_corfs(self):
        datas = {name: lf.openALV(name) for name in self.get_filelist()}
        self.cor_dict = {j: datas[j]["\"Correlation\""] for j in datas}
        # average over the count rates obtained from the two detectors
        self.counts_series_dict = {
            j: datas[j]["\"Count Rate\""] for j in datas}
        self.condis_dict = {j: lxf_conditions(j) for j in datas}
#		if self.condis_dict.values()[0]['Mode']!='SINGLE AUTO CH0': print("Use CorDataCal type instead")

    def __init__(self, filelist='!glob', path='', mask='*asc'):
        """
        Constructor method for CorDataSingleChannel, child of CorData, child of Data
        """
        super(LXFData, self).__init__(
            filelist, path, mask)  # call to constructor of at.Data, not CorData
        self._read_corfs()
        self._read_count_rates()
        self._read_condition(self.condis_dict, conditions=[
                             "T", "Theta", "lambda0", "q", "r_idx"])
        self._build_condis_vs_count_rates(self.condis_dict, conditions=["T"])


def format_plot(axis_labelsize=30, legend_fontsize=26, titlesize=26,
                x_maxticks=6, y_maxticks=5,
                maj_ticklength=10, maj_tickwidth=1, min_ticklength=4, min_tickwidth=1,
                ticklabelsize=26, tickpad=10, bottomroom=0.15, leftroom=0.20, preset="small",
                ax=None, fi=None, leg_pos=0, xlogbase=10, ylogbase=10, draw_legend=True,
                bothticksx=True, bothticksy=True, numpoints=1, frameon=False, ncol=1,
                **kwargs):
    """
    Gets the current figures and axes from pyplot and fits them into
    my personally preferred format by enlarging font sizes.
    """
    if ax == None:
        ax = pp.gca()
    if fi == None:
        fi = pp.gcf()
    h, l = ax.get_legend_handles_labels()
    # leg=ax.get_legend()
    if preset == "sfrey-plot-S_q.py":  # the set defaults will do a good job
        axis_labelsize = 30
        legend_fontsize = 20
        x_maxticks = 6
        y_maxticks = 5
        maj_ticklength = 10
        maj_tickwidth = 3
        min_ticklength = 3
        min_tickwidth = 2
        ticklabelsize = 20
        tickpad = 10
        bottomroom = 0.15
        preset = "small"
    if preset == "small":
        pass
    # if labels appear missing - change ax to pp
    ax.set_xlabel(ax.get_xlabel(), size=axis_labelsize)
    ax.set_ylabel(ax.get_ylabel(), size=axis_labelsize)
    ax.set_title(ax.get_title(), size=titlesize)
    # add location management when shit is no longer FUBAR
    if draw_legend:
        ax.legend(h, l, loc=leg_pos, frameon=frameon,
                  fontsize=legend_fontsize, numpoints=numpoints, ncol=ncol)
    if ax.get_xscale() == "linear":  # locator for log is automatically nice
        ax.xaxis.set_major_locator(MaxNLocator(x_maxticks))
        ax.xaxis.set_minor_locator(AutoMinorLocator())
    else:
        ax.xaxis.set_major_locator(LogLocator(numticks=15))
        ax.xaxis.set_minor_locator(LogLocator(
            numticks=15, subs=np.arange(2, 10)))
#
    if ax.get_yscale() == "linear":  # locator for log is automatically nice
        ax.yaxis.set_major_locator(MaxNLocator(y_maxticks))
        ax.yaxis.set_minor_locator(AutoMinorLocator())
    else:
        ax.yaxis.set_major_locator(LogLocator(numticks=15))
        ax.yaxis.set_minor_locator(LogLocator(
            numticks=15, subs=np.arange(2, 10)))

    #
    if bothticksx == True:
        ax.xaxis.set_ticks_position('both')
    if bothticksy == True:
        ax.yaxis.set_ticks_position('both')
    ax.xaxis.set_tick_params(length=maj_ticklength,
                             width=maj_tickwidth, direction='in')
    ax.yaxis.set_tick_params(length=maj_ticklength,
                             width=maj_tickwidth, direction='in')
    ax.tick_params(axis='x', which='minor', width=min_tickwidth,
                   length=min_ticklength, direction='in')
    ax.tick_params(axis='y', which='minor', width=min_tickwidth,
                   length=min_ticklength, direction='in')
    ax.tick_params(axis='both', which='major',
                   labelsize=ticklabelsize, pad=tickpad)
    fi.subplots_adjust(bottom=bottomroom)
    fi.subplots_adjust(left=leftroom)
#


def format_leg(ax, leg_pos, leg_fs, graphs, place='in', **kwargs):
    kwargs_defaults = {'boxscale': 0.8, 'rectscale': 0.9}
    labels = [l.get_label() for l in graphs]
    if place == 'in':
        ax.legend(graphs, labels, loc=leg_pos,
                  fontsize=leg_fs, numpoints=1, **kwargs)
    elif place == 'out':
        if 'bbox_to_anchor' not in kwargs:
            kwargs['bbox_to_anchor'] = (1, 0.5)

        if 'boxscale' in kwargs:
            boxscale = kwargs['boxscale']
            del kwargs['boxscale']
        else:
            boxscale = kwargs_defaults['boxscale']

        if 'rectscale' in kwargs:
            rectscale = kwargs['rectscale']
            del kwargs['rectscale']
        else:
            rectscale = kwargs_defaults['rectscale']

        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width*boxscale, box.height])
        ax.legend(graphs, labels, loc='center left', fontsize=leg_fs, **kwargs)
        pp.tight_layout(rect=[0, 0, rectscale, 1])


def format_ax(ax, fi, axis_labelsize=20, titlesize=20, legend_fontsize=20,
              x_maxticks=4, y_maxticks=4,
              maj_ticklength=10, maj_tickwidth=1, min_xticklength=5, min_xtickwidth=1,
              min_yticklength=5, min_ytickwidth=1,	
              ticklabelsize=20, tickpad=10, bottomroom=0.15, leftroom=0.20, preset="small",
              leg_pos=0, xlogbase=10, ylogbase=10, draw_legend=True, bothticksx=True, bothticksy=True,
              **kwargs):
    """
    Formats the given ax according to the parameters. Useful for plots with several, amongst other things.
    Does currently not perform any actions on the legend.
    """
    #
    ax.set_xlabel(ax.get_xlabel(), size=axis_labelsize)
    ax.set_ylabel(ax.get_ylabel(), size=axis_labelsize)
    ax.set_title(ax.get_title(), size=titlesize)
    if ax.get_xscale() == "linear":  # locator for log is automatically nice
        ax.xaxis.set_major_locator(MaxNLocator(x_maxticks))
        ax.xaxis.set_minor_locator(AutoMinorLocator())
    else:
        ax.xaxis.set_major_locator(LogLocator(base=xlogbase))
#
    if ax.get_yscale() == "linear":  # locator for log is automatically nice
        ax.yaxis.set_major_locator(MaxNLocator(y_maxticks))
        ax.yaxis.set_minor_locator(AutoMinorLocator())
    else:
        ax.yaxis.set_major_locator(LogLocator(base=ylogbase))
    #
    if bothticksx == True:
        ax.xaxis.set_ticks_position('both')
    if bothticksy == True:
        ax.yaxis.set_ticks_position('both')

    ax.xaxis.set_tick_params(length=maj_ticklength,
                             width=maj_tickwidth, direction='in')
    ax.yaxis.set_tick_params(length=maj_ticklength,
                             width=maj_tickwidth, direction='in')
    ax.tick_params(axis='x', which='minor', width=min_xtickwidth,
                   length=min_xticklength, direction='in')
    ax.tick_params(axis='y', which='minor', width=min_ytickwidth,
                   length=min_yticklength, direction='in')

    ax.tick_params(axis='both', which='major',
                   labelsize=ticklabelsize, pad=tickpad)
    fi.subplots_adjust(bottom=bottomroom)
    fi.subplots_adjust(left=leftroom)


def annotate_xaxis(xpos, lbl="", lw=2.5, fw='normal', start=pp.gca().get_ylim()[0]-0.1,
                   height=0.1, fs=25, ls='--', **kwargs):
    """
    Puts a vertical dashed line from y=-0.1 to y=height at the requested
    position on the x-axis with the text in lbl. lw means linewidth,
    fw means fontweight.
    """
    # btf is a method in matplotlib, originally "blended_transform_factory"
    # here it is used to keep the annotation at the same heights, regardless
    # of zooming or dragging around the canvas
    tf = btf(pp.gca().transData, pp.gca().transAxes)
    pp.axvline(xpos, -0.1, height, ls=ls, color='black', linewidth=2)
    pp.annotate(lbl, xy=(xpos, 0), xycoords=tf, xytext=(xpos, height+0.05),
                textcoords=tf, ha='center', va='center', fontsize=fs, fontweight=fw,
                **kwargs)
    #
#


def annotate_yaxis(ypos, lbl="", lw=2.5, fw='normal',
                   length=0.1, fs=25, ls='--', start=-0.1, push=1.25, linecolor='k', **kwargs):
    """
    Puts a horizontal dashed line from x=-0.1 (relative to xlim) to x=length at the
    requested postion on the y-axis with the text in lbl. lw means inewidth,
    fw means fontweight.
    """
    # btf is a method in matplotlib, originally "blended_transform_factory"
    # here it is used to keep the annotation at the same heights, regardless
    # of zooming or dragging around the canvas
    tf = btf(pp.gca().transData, pp.gca().transAxes)
    l = pp.axhline(ypos, start, length, ls=ls, color=linecolor, linewidth=2)
    length_txt = (pp.gca().get_xlim()[1]-pp.gca().get_xlim()[0])*length
    pp.annotate(lbl, xy=(push, 1), xycoords=l,
                fontsize=fs, fontweight=fw, va='center', ha='center',
                **kwargs)
    #
#

def wrt_condis( path=os.getcwd(), fn=os.getcwd().split('\\')[-1]+'.out' ):
    """
    Navigate to a folder and call wrt_condis to write the ALV conditions to a table
    with the filename as an index
    """

    data=LXFDataCal()
    
    crs=data.get_counts_series_dict()
    condis=data.get_condis_dict()
  
    lf.write_dct(condis, fn)
    print(path+"\\"+fn) 
    
    return { path+"\\"+fn : pd.read_csv(fn, header=0, sep="\t", comment="#") }

# palette generators
def clr(dct, cmap=lf.cmapvir):
    idcs=[i for i in dct]
    clrs={ idcs[i]:cmap( int(np.floor(i*((255+255/(len(idcs)-1))/(len(idcs)-1)))) ) for i in range(0, len(idcs)) }
    return clrs

def clr_discrete(dct, cmap=colormaps.get("Set2")):
    idcs=[i for i in dct]
    clrs={ idcs[i]:cmap( i ) for i in range(0, len(idcs)) }
    return clrs

def etaDLS_monexp(mask, R, alias, legend=False, parlst=[('A', 0.8, True, 0.7, 1.0),('beta', 1e2, True, 1e-3, 1e3)], fnc=fn.monoexp, etapar='beta', ymin=0.1):
    lxfi=LXFDataCal(mask=mask)
    
    crs=lxfi.get_counts_series_dict()
    condis=lxfi.get_condis_dict()
    crfs=lxfi.get_cordict()
    
    clrs=clr_discrete(crfs,)
    
    fig,ax=pp.subplots(layout='constrained')
    
    lf.mrks.reset()
    lf.clrs.reset()
    
    g2min1={ i:np.vstack([crfs[i][3:,0]*1e-3, np.sqrt(crfs[i][3:,1])]).transpose() for i in crfs }
    
    [ax.plot(g2min1[i][:,0], g2min1[i][:,1], \
            markevery=3, mec=clrs[i], marker=lf.mrks.next(), lw=0, ms=8, mfc='None', label=i) for i in g2min1]
    
    pars={}
    fits={}
    rslpars={}
    
    for i in crfs:
        pars[i]=lm.Parameters()
        pars[i].add_many(*parlst)
        rstr=lf.chopy(g2min1[i][:], (ymin,1) )
        fits[i]=lm.minimize( fnc, pars[i], args=(rstr[:,0], rstr[:,1]) )
        rslpars[i]=fits[i].params
        [ax.plot(g2min1[i][:,0], fnc(rslpars[i], g2min1[i][:,0]), ms=0, lw=2, c=clrs[i]) for i in fits]
    
    if legend: ax.legend(frameon=False)
    ax.set_ylim((0,1))
    ax.set_xscale('log')
    ax.set_title('$\Theta=${}$^\circ$, $T=${} $^\circ C$'.format(round(condis[i]['Theta']), round(condis[i]['T'])))    
    rsls={}
    clcs={}
    for i in crfs:
        rsls[i]={}
        clcs[i]={}
        for j in rslpars[i]:
            rsls[i][j]=rslpars[i][j].value
            rsls[i][j+'_stderr']=rslpars[i][j].stderr
        clcs[i]['tauA']=1/rsls[i][etapar]
        clcs[i]['etaA']=lf.gamma_to_eta([rsls[i][etapar]], condis[i]['T'], condis[i]['q'], R)[0]
    
        rsls[i]=lf.mrgdct(lf.mrgdct(rsls[i], clcs[i]), condis[i])

    format_ax(ax,fig)

    ax.set_xlabel('$\\tau$ (s)')
    ax.set_ylabel('$\sqrt{g_2-1}$ (-)')
    fig.savefig(alias+'.png', dpi=600)
    lf.write_dct(rsls, alias+'.out')
    lf.write_stacked_dct(crfs, condis)

    return rsls,ax,fig

