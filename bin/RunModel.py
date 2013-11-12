#!/usr/bin/env python
"""@package RunModel

@brief Run RHESSys

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2013, University of North Carolina at Chapel Hill
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
1. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   rhessys_dir
   rhessys_bin

Post conditions
---------------
1. Will write an entry to the model run section of the project metadata

2. Will write an entry to the history section of the project metadata when the model run sucessfully completes

Usage:
@code
RunModel.py -p /path/to/project_dir -d "Scenario 1" (--basin | --hillslope | --zone | --patch | --canopy) -pre OUTPUT_PREFIX -st YYYY M D H -ed YYYY M D H -w WORLDFILE -t TECFILE -r FLOWTABLE [SURFACE_FLOWTABLE] [-- RHESSYS_ARG_1 ... RHESSYS_ARG_N]
@endcode
"""
import os
import sys
import errno
import argparse
import textwrap
import datetime
import subprocess

import ecohydrolib.util

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.metadata import ModelRun
from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.rhessys import generateCommandString

# Handle command line options
parser = argparse.ArgumentParser(description='Run RHESSys, recording information about the run in metadata')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='Print detailed information about what the program is doing')
parser.add_argument('-d', '--description', dest='description', required=True,
                    help='Description of the model run')
parser.add_argument('-pre', dest='outputPrefix', required=True,
                    help='Filename prefix to use for output files, relative to output directory in the RHESSys directory of the project')
parser.add_argument('-st', dest='startDate', required=True, nargs=4, type=int,
                    help='Start date and time of the model run, of the form "YYYY M D H"')
parser.add_argument('-ed', dest='endDate', required=True, nargs=4, type=int,
                    help='Date date and time of the model run, of the form "YYYY M D H"')
parser.add_argument('-w', dest='worldfile', required=True,
                    help='Filename of the worldfile to use for the model run, specified relative to the worldfiles directory in the RHESSys directory of the project')
parser.add_argument('-t', dest='tecfile', required=True,
                    help='Filename of the tecfile to use for the model run, specified relative to the tec directory in the RHESSys directory of the project')
parser.add_argument('-r', dest='flowtables', required=False, nargs='*',
                    help='Filename(s) of the flow table(s) to use for the model run, specified relative to the flowtable directory in the RHESSys directory of the project. ' +
                         'If one flow table is supplied, it will be used for subsurface and surface routing.  ' +
                         'If two flow tables are supplied the first will be use for subsurface routing, the second for surface.')
outputType = parser.add_mutually_exclusive_group(required=True)
outputType.add_argument('--basin', dest='outputType', action='store_const', const='-b',
                        help='Tell RHESSys to output at the basin spatial level')
outputType.add_argument('--hillslope', dest='outputType', action='store_const', const='-h',
                        help='Tell RHESSys to output at the hillslope spatial level')
outputType.add_argument('--zone', dest='outputType', action='store_const', const='-z',
                        help='Tell RHESSys to output at the zone spatial level')
outputType.add_argument('--patch', dest='outputType', action='store_const', const='-p',
                        help='Tell RHESSys to output at the patch spatial level')
outputType.add_argument('--canopy', dest='outputType', action='store_const', const='-c',
                        help='Tell RHESSys to output at the canopy stratum spatial level')
parser.add_argument('args', nargs=argparse.REMAINDER)
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
try:
    configFile = args.configfile
except AttributeError:
    pass

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'rhessys_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys directory" % (context.projectDir,))
if not 'rhessys_bin' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys binary" % (context.projectDir,))

# Make sure specified files exist
rhessysDir = metadata['rhessys_dir']
paths = RHESSysPaths(args.projectDir, rhessysDir)

rhessysBinPathRel = metadata['rhessys_bin']
rhessysBinPath = os.path.join(context.projectDir, rhessysBinPathRel)
if not os.path.isfile(rhessysBinPath) or not os.access(rhessysBinPath, os.X_OK):
    sys.exit("Putative RHESSys executable '%s' is not an executable file" % (rhessysBinPath,) )

if args.outputPrefix.count(os.sep) > 1:
    sys.exit("Output prefix cannot contain a path separator ('%s')" % (args.outputPrefix,) )
if not os.access(paths.RHESSYS_OUT, os.W_OK):
    sys.exit("RHESSys output directory '%s' is not writable" % (paths.RHESSYS_OUT,) )
outputDir = os.path.join(paths.RHESSYS_OUT, args.outputPrefix)
# Append path separator and 'rhessys' so that RHESSys will write output into a subdirectory
outputPrefix = os.path.join(outputDir, RHESSysMetadata.MODEL_NAME)
if os.path.isdir(outputPrefix):
    sys.exit( textwrap.fill("\nOutput directory '%s' already exists, please choose another output prefix." % (outputPrefix,) ) )
outputPrefixRel = paths.relpath(outputPrefix)
outputDirRel = paths.relpath(outputDir)

if args.worldfile.count(os.sep) > 1:
    sys.exit("Worldfile cannot contain a path separator ('%s')" % (args.worldfile,) )
worldfile = os.path.join(paths.RHESSYS_WORLD, args.worldfile)
if not os.path.isfile(worldfile) or not os.access(worldfile, os.R_OK):
    sys.exit("Worldfile '%s' is not a readable file" % (worldfile,) )
worldfileRel = paths.relpath(worldfile)
    
if args.tecfile.count(os.sep) > 1:
    sys.exit("TEC file cannot contain a path separator ('%s')" % (args.tecfile,) )
tecfile = os.path.join(paths.RHESSYS_TEC, args.tecfile)
if not os.path.isfile(tecfile) or not os.access(tecfile, os.R_OK):
    sys.exit("TEC file '%s' is not a readable file" % (tecfile,) )
tecfileRel = paths.relpath(tecfile)

if args.flowtables:
    # We are running in routing mode
    cmd_proto = "{bin} -st {startDate} -ed {endDate} {outputType} -pre {outputPrefix} -t {tecfile} -w {worldfile} -r {flowtables} {remainders}"

    surfaceFlow = None
    subsurfaceFlow = args.flowtables[0]
    if subsurfaceFlow.count(os.sep) > 1:
        sys.exit("Flowtable cannot contain a path separator ('%s')" % (subsurfaceFlow,) )
    subsurfaceFlow = os.path.join(paths.RHESSYS_FLOW, subsurfaceFlow)
    if not os.path.isfile(subsurfaceFlow) or not os.access(subsurfaceFlow, os.R_OK):
        sys.exit("Flowtable '%s' is not a readable file" % (subsurfaceFlow,) )
    subsurfaceFlowRel = paths.relpath(subsurfaceFlow)
    flowtables = subsurfaceFlow
    flowtablesRel = subsurfaceFlowRel
        
    if len(args.flowtables) == 2:
        surfaceFlow = args.flowtables[1]
        if surfaceFlow.count(os.sep) > 1:
            sys.exit("Surface flowtable cannot contain a path separator ('%s')" % (surfaceFlow,) )
        surfaceFlow = os.path.join(paths.RHESSYS_FLOW, surfaceFlow)
        if not os.path.isfile(surfaceFlow) or not os.access(surfaceFlow, os.R_OK):
            sys.exit("Surface flowtable '%s' is not a readable file" % (surfaceFlow,) )
        surfaceFlowRel = paths.relpath(surfaceFlow)
        flowtables += ' ' + surfaceFlow
        flowtablesRel += ' ' + surfaceFlowRel
else:
    # We are running in topmodel mode
    cmd_proto = "{bin} -st {startDate} -ed {endDate} {outputType} -pre {outputPrefix} -t {tecfile} -w {worldfile} {remainders}"
    flowtables = flowtablesRel = None

remainders = ' '.join(args.args[1:])
startDate = ' '.join([str(d) for d in args.startDate])
endDate = ' '.join([str(d) for d in args.endDate])

# Build command string for running (i.e. with absolute paths)
cmd = cmd_proto.format(bin=rhessysBinPath, startDate=startDate, endDate=endDate,
                       outputType=args.outputType, outputPrefix=outputPrefix,
                       tecfile=tecfile, worldfile=worldfile, flowtables=flowtables, remainders=remainders)
# Build command string with relative paths for metadata
cmdRel = cmd_proto.format(bin=rhessysBinPathRel, startDate=startDate, endDate=endDate,
                       outputType=args.outputType, outputPrefix=outputPrefixRel,
                       tecfile=tecfileRel, worldfile=worldfileRel, flowtables=flowtablesRel, remainders=remainders)

# Run RHESSys
sys.stdout.write("Running RHESSys...")

cmdArgs = cmd.split()
process = subprocess.Popen(cmdArgs, cwd=paths.RHESSYS_DIR, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# Create output directory so we can store RHESSys output there
os.makedirs(outputDir)
rhessysOutPath = os.path.join(outputDir, 'rhessys.out')
rhessysOut = open(rhessysOutPath, 'w')

# Get output
while True:
    line = process.stdout.readline()
    if not line:
        break
    rhessysOut.write(line)
    if args.verbose:
        sys.stdout.write(line)

if process.wait() != 0:
    sys.exit("\n\nRHESSys failed, returning %s" % (process.returncode,) )

rhessysOut.close() 
print('\n\nRHESSys model run successfully completed\n')

# Write metadata about run
run = ModelRun()
run.description = args.description
run.date = datetime.datetime.utcnow()
run.command = cmdRel
run.output = outputDirRel
run.writeToMetadata(context)

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)

