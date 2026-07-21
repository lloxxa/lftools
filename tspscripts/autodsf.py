#!/anaconda/bin/python
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  5 19:50:11 2015

@author: aljosha

autodsf.py

autodsf.py <command_line_tool> <input_file>

Automate analysis of <command_line_tool> with the settings supplied by <input_file>.

Supported <command_line_tool>s: strufa_dyn_mq2.exe

Format input files as follows for strufa_dynmq2.exe: 
    <dir> <mask> <samp> <weed> <plng> <qlis> <dq> <max_mem> <opfx>
    <samp>: either "lin" or "log"
    <plng>: polymer length
    <qlis>: q-list, supplied as [value1, value2, value3, ..., valueN]
    <opfx>: path+prefix to which job-specific info will be appended
    to construct an filename for output storage
"""
import sys
import autotools as at
import autotools_dummy_objects as atd

def main(argv):
    if len(argv) < 2:
        print("Usage: autodsf.py <command_line_tool> <input_file>")
        sys.exit()
    #
    command_line_tool=argv[0]
    input_file=argv[1]
    if command_line_tool=="strufa_dynmq2.exe":    
        dsfjob=at.DsfJob(input_file, DataClass=atd.TrajectoriesDummy)
        dsfjob.call()
    else:
        print("<command_line_tool> not recognized. autodsf.py will exit.")
        print("Usage: autodsf.py <command_line_tool> <input_file>")
        sys.exit()
    #
#
if __name__ == "__main__":
    main(sys.argv[1:])