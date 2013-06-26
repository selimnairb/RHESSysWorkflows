#!/usr/bin/env python
"""@package ImportRoofConnectivityMapIntoGRASS

@brief Import roof raster map into a GRASS location and generate 
connectivity map.

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

2. The following metadata entry(ies) must be present in the manifest section of the metadata associated with the project directory:
   roof_connectivity
   
3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   
Post conditions
---------------
1. Will write the following entry(ies) to the GRASS section of metadata associated with the project directory:
   roofs_rast

Usage:
@code
ImportRoofConnectivityMapIntoGRASS.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys, errno, shutil
import argparse
#import ConfigParser

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Generate roof connectivity map in GRASS GIS. Roof map should, defined by roof_connectivity raster, should be an floating point raster with values [0-1] representing proportion of flow from each roof pixel that should be routed to the nearest impervious surface; all other values NULL.')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
manifest = RHESSysMetadata.readManifestEntries(context)
if not 'roof_connectivity' in manifest:
    sys.exit("Metadata in project directory %s does not contain a roof_connectivity raster" % (context.projectDir,))

metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

# Import roof_connectivity raster map into GRASS
roofRasterPath = os.path.join(context.projectDir, manifest['roof_connectivity'])
result = grassLib.script.run_command('r.in.gdal', input=roofRasterPath, output='roofs', overwrite=args.overwrite)
if result != 0:
    sys.exit("Failed to import roof connectivity raster into GRASS dataset %s/%s, result:\n%s" % \
             (grassDbase, metadata['grass_location'], result) )
RHESSysMetadata.writeGRASSEntry(context, 'roofs_rast', 'roofs')

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)