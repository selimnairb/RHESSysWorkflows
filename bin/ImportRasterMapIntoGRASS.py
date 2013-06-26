#!/usr/bin/env python
"""@package ImportRasterMapIntoGRASS

@brief Import raster map already registered in metadata via EcohydroLib.RegisterRaster, into GRASS.
Raster type must be one of RHESSysMetadata.RASTER_TYPES.

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

2. One or more of the following metadata entry(ies) must be present in the manifest section of the metadata associated with the project directory:
   rhessysworkflows.metadata.RASTER_TYPES, currently:
   landcover
   roof_connectivity
   soil
   lai
   
3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   
Post conditions
---------------
1. Will write one or more the following entry(ies) to the GRASS section of metadata associated with the project directory:
   landcover_rast
   roof_connectivity_rast
   soil_rast
   lai_rast

Usage:
@code
ImportRasterMapIntoGRASS.py -t RASTER_TYPE_1 [RASTER_TYPE_2 ... RASTER_TYPE_N] -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys
import argparse

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
typeChoices = list(RHESSysMetadata.RASTER_TYPES)
typeChoices.insert(0, 'all')
parser = argparse.ArgumentParser(description='Import raster map already registered in metadata via EcohydroLib.RegisterRaster, into GRASS. Raster type must be one of RHESSysMetadata.RASTER_TYPES.')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-t', '--type', dest='types', required=True, nargs='+', choices=typeChoices,
                    help='The type of raster dataset to import, or all if all types should be imported.')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

if 'all' in args.types:
    typeList = RHESSysMetadata.RASTER_TYPES
else:
    typeList = args.types

## Check for necessary information in metadata
manifest = RHESSysMetadata.readManifestEntries(context)
#for type in typeList:
#    if not type in manifest:
#        sys.exit("Metadata in project directory %s does not contain a %s raster" % (context.projectDir, type))

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

# Import raster maps into GRASS
for type in typeList:
    if type in manifest:
        sys.stdout.write("Importing %s raster..." % (type,) )
        sys.stdout.flush()
        rasterPath = os.path.join(context.projectDir, manifest[type])
        result = grassLib.script.run_command('r.in.gdal', input=rasterPath, output=type, overwrite=args.overwrite)
        if result != 0:
            sys.exit("Failed to import raster %s into GRASS dataset %s/%s, result:\n%s" % \
                     (type, grassDbase, metadata['grass_location'], result) )
        grassEntryKey = "%s_rast" % (type,)
        RHESSysMetadata.writeGRASSEntry(context, grassEntryKey, type)
        sys.stdout.write('done\n')

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)