import tools as ts
import matplotlib.pyplot as pp
import numpy as np
import sys
import os
from matplotlib.ticker import AutoMinorLocator, MaxNLocator, LogLocator
from matplotlib.transforms import blended_transform_factory as btf
from matplotlib import rc


#rc('font',**{'family':'monospace','monospace':['Computer Modern Typewriter']})
#rc('text', usetex=True)


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


def format_ax(ax, fi, axis_labelsize=30, titlesize=24, legend_fontsize=26,
              x_maxticks=6, y_maxticks=5,
              maj_ticklength=10, maj_tickwidth=1, min_ticklength=5, min_tickwidth=1,
              ticklabelsize=26, tickpad=10, bottomroom=0.15, leftroom=0.20, preset="small",
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
    ax.tick_params(axis='x', which='minor', width=min_tickwidth,
                   length=min_ticklength, direction='in')
    ax.tick_params(axis='y', which='minor', width=min_tickwidth,
                   length=min_ticklength, direction='in')

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
