#!/usr/bin/env python
"""@package PatchToCumulativeValues

@brief Tool for printing cummulative values of patch-scale RHESSys output variables.

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2014, University of North Carolina at Chapel Hill
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the University of North Carolina at Chapel Hill nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE UNIVERSITY OF NORTH CAROLINA AT CHAPEL HILL
BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR 
CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT 
LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


@author Brian Miles <brian_miles@unc.edu>


Pre conditions
--------------
1. Configuration file must define the following sections and values:
   'GRASS', 'GISBASE'
   'RHESSYS', 'PATH_OF_FFMPEG'

2. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset


Post conditions
---------------
None
   
@todo Add ability to read in two files, accumulate data, and write normalized map (value / max(value))   

"""
import os, sys, shutil, tempfile, re
import subprocess, shlex
import time, random
import argparse
import operator
import datetime

import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt

from ecohydrolib.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from ecohydrolib.grasslib import *

from rhessysworkflows.rhessys import RHESSysOutput

# Handle command line options
parser = argparse.ArgumentParser(description='Generate cummulative map of patch-scale RHESSys output variables')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file.')
parser.add_argument('-d', '--rhessysOutFile', required=True, nargs='+',
                    help='Directory containing RHESSys patch output, specificically patch daily output stored in a file whose name ends with "_patch.daily".')
parser.add_argument('-v', '--outputVariables', required=True, nargs='+',
                    help='Name of RHESSys variables to be mapped.  Should be a list of individual variable names, not expressions thereof')
parser.add_argument('-p', '--patchIDs', required=True, nargs='+', type=int,
                    help='Patches for which output should be produced')
parser.add_argument('--startdate', type=int, nargs=4,
                    help='Date on which to begin output, of format YYYY M D H')
parser.add_argument('--enddate', type=int, nargs=4,
                    help='Date on which to end output, of format YYYY M D H')
args = parser.parse_args()

startDate = None
if args.startdate:
    # Set end date based on command line
    startDate = datetime.datetime(args.startdate[0],
                                  args.startdate[1],
                                  args.startdate[2],
                                  args.startdate[3])

endDate = None
if args.enddate:
    # Set end date based on command line
    endDate = datetime.datetime(args.enddate[0],
                                args.enddate[1],
                                args.enddate[2],
                                args.enddate[3])

patchDailyFilepaths = []
for outfile in args.rhessysOutFile:
    if not os.path.isfile(outfile) or not os.access(outfile, os.R_OK):
        sys.exit("Unable to read RHESSys output file %s" % (outfile,))
    patchDailyFilepaths.append( os.path.abspath(outfile) ) 

# Determine output variables
variables = ['patchID'] + args.outputVariables

sys.stdout.write('scenario,patchid')
for var in args.outputVariables:
    sys.stdout.write(',sum_' + var)
sys.stdout.write('\n')

# For each rhessys output file ...
for (i, patchDailyFilepath) in enumerate(patchDailyFilepaths):
    
    scenario = os.path.basename( os.path.dirname(patchDailyFilepath) )
    
    f = open(patchDailyFilepath)
    data = RHESSysOutput.readColumnsFromPatchDailyFile(f, variables)
    f.close()
    if len(data) < 1:
        sys.exit("No data found for variable in RHESSys output file '%s'" % \
                 (patchDailyFilepath,) )
    
    # For each day
    variablesDict = {}
    patchIDs = None
    variable = None
    for (i, key) in enumerate(data):
        if startDate and key < startDate:
            continue
        if endDate and key > endDate:
            break
        #import pdb; pdb.set_trace()
        dataForDate = data[key]
        vars = {}
        for var in args.outputVariables:
            vars[var] = np.array( dataForDate[var] )
        patchIDs = np.array( [ int(f) for f in dataForDate['patchID'] ] )
        
        # Store value for each selected patchID
        for p in args.patchIDs:
            try:
                dataForPatch = variablesDict[p]
            except KeyError:
                dataForPatch = {}
                variablesDict[p] = dataForPatch
            patchIdx = np.where( patchIDs == p )
            
            for var in args.outputVariables:
                variable = vars[var]
                try:
                    tmp_data = dataForPatch[var]
                except KeyError:
                    tmp_data = []
                    dataForPatch[var] = tmp_data
                tmp_data.append( variable[patchIdx] )
    
    # Print summary for each patch
    for p in args.patchIDs:
        dataForPatch = variablesDict[p]
        sys.stdout.write("%s,%d" % (scenario, p) )
        for var in args.outputVariables:
            p_tmp = np.array( dataForPatch[var] )
            sys.stdout.write(",%f" % (  p_tmp.sum() ) )
        sys.stdout.write('\n')
    
