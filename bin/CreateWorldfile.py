#!/usr/bin/env python
"""@package CreateWorldfile

@brief Create RHESSys worldfile.  This will create an initial worldfile used for input into the
lairead utility, which initializes vegetation carbon stores.

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
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   g2w_bin
   rat_bin
   template

   
Post conditions
---------------
1. Worldfile will be created in the RHESSys folder of the project directory.

2. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   worldfile_zero

Usage:
@code
CreateWorldfile.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import string
import re
import argparse
from subprocess import *

from ecohydrolib.grasslib import *
from ecohydrolib.spatialdata.utils import bboxFromString
from ecohydrolib.spatialdata.utils import calculateBoundingBoxCenter

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.rhessys import readParameterFile

# Handle command line options
parser = argparse.ArgumentParser(description='Create RHESSys worldfile using GRASS GIS data and grass2world utility')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='Print detailed information about what the program is doing')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
grassMetadata = RHESSysMetadata.readGRASSEntries(context)
if not 'dem_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a DEM raster in a GRASS mapset" % (context.projectDir,)) 
if not 'soil_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a soil raster in a GRASS mapset" % (context.projectDir,))
if not 'patch_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a patch raster in a GRASS mapset" % (context.projectDir,))

metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))
if not 'rhessys_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys directory" % (context.projectDir,))
if not 'g2w_bin' in metadata:
    sys.exit("Metadata in project directory %s does not contain a grass2world executable" % (context.projectDir,))
if not 'rat_bin' in metadata:
    sys.exit("Metadata in project directory %s does not contain an AverageTables executable" % (context.projectDir,))
if not 'template' in metadata:
    sys.exit("Metadata in project directory %s does not contain an world template" % (context.projectDir,))

rhessysDir = metadata['rhessys_dir']
paths = RHESSysPaths(args.projectDir, rhessysDir)

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

## Run grass2world
# Make sure mask and region are properly set
demRast = grassMetadata['dem_rast']
result = grassLib.script.run_command('g.region', rast=demRast)
if result != 0:
    sys.exit("g.region failed to set region to DEM, returning %s" % (result,))

basinRast = grassMetadata['basin_rast']
result = grassLib.script.run_command('r.mask', flags='o', input=basinRast, maskcats='1')
if result != 0:
    sys.exit("r.mask failed to set mask to basin, returning %s" % (result,))

templateFilename = os.path.basename( metadata['template'] )
templateFilepath = os.path.join( context.projectDir, metadata['template'] )

worldfileName = "%s_init" % (templateFilename.replace('template', 'world'), )
worldfilePath = os.path.join(paths.RHESSYS_WORLD, worldfileName)

g2wPath = os.path.join(context.projectDir, metadata['g2w_bin'])
g2wCommand = "%s -t %s -w %s" % (g2wPath, templateFilepath, worldfilePath)

# Make sure g2w can find rat
g2wEnv = dict(os.environ)
g2wEnv['PATH'] = paths.RHESSYS_BIN + os.pathsep + g2wEnv['PATH']

if args.verbose:
    print(g2wCommand)
sys.stdout.write("\nRunning grass2world from %s..." % (paths.RHESSYS_BIN,) )
sys.stdout.flush()
cmdArgs = g2wCommand.split()
process = Popen(cmdArgs, cwd=paths.RHESSYS_BIN, env=g2wEnv, 
                stdout=PIPE, stderr=PIPE)
(process_stdout, process_stderr) = process.communicate()
if args.verbose:
    sys.stdout.write(process_stdout)
    sys.stderr.write(process_stderr)
if process.returncode != 0:
    sys.exit("\n\ngrass2world failed, returning %s" % (process.returncode,) )    

RHESSysMetadata.writeRHESSysEntry(context, 'worldfile_zero', paths.relpath(worldfilePath) )

sys.stdout.write('\n\nFinished creating worldfile\n')

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)
