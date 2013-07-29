#!/usr/bin/env python
"""@package GenerateBaseStationMap

@brief Generate climate base station raster map in GRASS for a list of base stations 
using Thiessen polygons.

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
1. Configuration file must define the following sections and values:
   'GRASS', 'GISBASE'
   
2. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   
Post conditions
---------------
1. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   basestations_text

2. Will write the following entry(ies) to the GRASS section of metadata associated with the project directory:
   basestations_rast
 
Usage:
@code
GenerateBaseStationMap.py -p /path/to/project_dir -b /path/to/base/station/file
@endcode

@note GRASS v.voronoi routine used to generate Thiessen polygons has difficulties when there are
only two points.  This may be fixed in GRASS 6.4.3.  Until then, do not use two climate stations.

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys, shutil
import argparse

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Generate climate base station raster map in GRASS for a list of base stations using Thiessen polygons.')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-b', '--basestationsFile', dest='basestationsFile', required=True,
                    help='Text file of the form: id|easting|northing|name')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

if not os.path.isfile(args.basestationsFile):
    sys.exit("Specified base stations file '%s' is not a file" % (args.basestationsFile,) )
if not os.access(args.basestationsFile, os.R_OK):
    sys.exit("Specified base stations file '%s' is not readable" % (args.basestationsFile,) )

# Check for necessary information in metadata
metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))
if not 'rhessys_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys directory" % (context.projectDir,))

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])

# Get path of place to store climate data
projectDirClimDir = paths.RHESSYS_CLIM

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)    

# Copy base stations file into project directory
basestationsDest = os.path.join(projectDirClimDir, 'basestations.txt')
shutil.copyfile(args.basestationsFile, basestationsDest)

# Import base station points
p = grassLib.script.pipe_command('v.in.ascii', input=basestationsDest, out='basestation_points', x=2, y=3, cat=1,
                                 columns='cat int, x double precision, y double precision, name varchar(15)',
                                 overwrite=args.overwrite)
(stdoutStr, stderrStr) = p.communicate() 
result = p.returncode
if result != 0:
    sys.stdout.write(stdoutStr)
    sys.exit("\nv.in.ascii failed, returning %s" % (result,))
    
# Generate Thiessen polygons
p = grassLib.script.pipe_command('v.voronoi', input='basestation_points', output='basestation_areas', 
                                 overwrite=args.overwrite)
(stdoutStr, stderrStr) = p.communicate() 
result = p.returncode
if result != 0:
    sys.stdout.write(stdoutStr)
    sys.exit("\nv.voronoi failed, returning %s" % (result,))

# Rasterize Thiessen polygons
p = grassLib.script.pipe_command('v.to.rast', input='basestation_areas', output='basestations', 
                                 use='cat', labelcolumn='name', overwrite=args.overwrite)
(stdoutStr, stderrStr) = p.communicate() 
result = p.returncode
if result != 0:
    sys.stdout.write(stdoutStr)
    sys.exit("\nv.to.rast failed, returning %s" % (result,))

# Write metadata 
RHESSysMetadata.writeRHESSysEntry( context, 'basestations_text', paths.relpath(basestationsDest) )
RHESSysMetadata.writeGRASSEntry( context, 'basestations_rast', 'basestations' )

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)
