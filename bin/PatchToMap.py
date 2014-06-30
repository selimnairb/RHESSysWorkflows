#!/usr/bin/env python
"""@package PatchToMap

@brief Tool for mapping patch-scale RHESSys yearly output variables.

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

2. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset


Post conditions
---------------
None

"""
import os, sys, shutil, tempfile, re
import subprocess, shlex
import time, random
import argparse
import operator
import math

import numpy as np
import statsmodels.api as sm
import matplotlib
import matplotlib.pyplot as plt

from ecohydrolib.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from ecohydrolib.grasslib import *

from rhessysworkflows.rhessys import RHESSysOutput



INT_RESCALE = 100
VARIABLE_EXPR_RE = re.compile(r'\b([a-zA-z][a-zA-Z0-9_\.]+)\b') # variable names can have "." in them
RANDOM = random.randint(100000, 999999)
RECLASS_MAP_TMP = "patchzonalstats_cover_{0}".format(RANDOM)
STATS_MAP_TMP = "patchzonalstats_output_{0}".format(RANDOM)

methods = ['average', 'mode', 'median', 'avedev', 'stddev', 'variance',
           'skewness', 'kurtosis', 'min', 'max', 'sum']

# Handle command line options
parser = argparse.ArgumentParser(description='Generate cummulative map of patch-scale RHESSys output variables')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file.')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-d', '--rhessysOutFile', required=True, nargs='+',
                    help='Directory containing RHESSys patch output, ' +\
                         'specificically patch yearly output in a file ending in "_patch.yearly".')
parser.add_argument('--mask', required=False, default=None,
                    help='Name of raster to use as a mask')
parser.add_argument('--patchMap', required=False, default='patch',
                    help='Name of patch map')
parser.add_argument('-y', '--year', required=False, type=int,
                    help='Year for which statistics should be generated')
parser.add_argument('-v', '--outputVariable', required=True,
                    help='Name of RHESSys variable to be mapped.  Can be an expression such as "trans_sat + trans_unsat"')
parser.add_argument('-n', '--mapNames', required=True, nargs='+',
                    help='Names of maps to be created.')
parser.add_argument('--mapcolorstyle', required=False, default='grey1.0',
                    help='Color map style to pass to r.colors, used for zonal stats map.')
args = parser.parse_args()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile)

if not len(args.rhessysOutFile) == len(args.mapNames):
    sys.exit("Number of RHESSys output files must match the number of map names")

# Check for necessary information in metadata
metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))

patchFilepaths = []
for outfile in args.rhessysOutFile:
    if not os.path.isfile(outfile) or not os.access(outfile, os.R_OK):
        sys.exit("Unable to read RHESSys output file %s" % (outfile,))
    patchFilepaths.append( os.path.abspath(outfile) ) 

# Determine output variables
variables = ['patchID']
m = VARIABLE_EXPR_RE.findall(args.outputVariable)
if m:
    variables += m
else:
    sys.exit("No output variables specified")

# 1. Get tmp folder for temprarily storing rules
tmpDir = tempfile.mkdtemp()
print("Temp dir: %s" % (tmpDir,) )
reclassRule = os.path.join(tmpDir, 'reclass.rule')

# 2. Initialize GRASS
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

# Set mask (if present)
if args.mask:
    result = grassLib.script.run_command('r.mask',
                                         input=args.mask,
                                         maskcats="1",
                                         flags="o")
    if result != 0:
        sys.exit("Failed to set mask using layer %s" % (args.mask,) )
    # Zoom to map extent
    result = grassLib.script.run_command('g.region',
                                         rast='MASK',
                                         zoom='MASK')
    if result != 0:
        sys.exit("Failed to set region to layer %s" % \
                 (args.mask,) )

# 3. For each rhessys output file read variable(s) of interest...
variablesList = []
for (i, patchFilepath) in enumerate(patchFilepaths):
    print("\nReading RHESSys output %s from %s  (this may take a while)...\n" \
          % (os.path.basename(patchFilepath), os.path.dirname(patchFilepath)) )
    data = np.genfromtxt(patchFilepath, names=True)
    if len(data) < 1:
        sys.exit("No data found for variable in RHESSys output file '%s'" % \
                 (patchFilepath,) )
    
    if args.year:
        data = data[data['year'] == float(args.year)]
    
    patchIDs = [ int(p) for p in data['patchID'] ]
    expr = VARIABLE_EXPR_RE.sub(r'data["\1"]', args.outputVariable)
    variablesList.append(eval(expr))
        
# 4. Write maps for each input file
for (i, variable) in enumerate(variablesList):
    reclass_map = args.mapNames[i]
    # Write reclass rule to temp file
    reclass = open(reclassRule, 'w') 
    for (j, var) in enumerate(variable):
        reclass.write("%d:%d:%f:%f\n" % (patchIDs[j], patchIDs[j], var, var) )
    reclass.close()
        
    # Generate map for variable
    print("\nMapping variable: {0} for input {1} to map named {2}...".format(args.outputVariable, 
                                                                              patchFilepaths[i],
                                                                              reclass_map))
    result = grassLib.script.run_command('r.recode', 
                                         input=args.patchMap, 
                                         output=reclass_map,
                                         rules=reclassRule,
                                         flags='d',
                                         overwrite=True)
    if result != 0:
        sys.exit("Failed to create reclass map {0}".format(reclass_map) )
        
    # Set color table
    if args.mapcolorstyle:
        result = grassLib.script.run_command('r.colors', 
                                             map=reclass_map,
                                             color=args.mapcolorstyle)
        if result != 0:
            sys.exit("Failed to modify color map")

# Cleanup
shutil.rmtree(tmpDir)

