#!/usr/bin/env python
"""@package RunLAIRead

@brief Run lairead utility to initializes vegetation carbon stores. Will: (1) run lairead to
produce a redefine worldfile; (2) run RHESSys simulation for 3-days to generate base worldfile

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
   lairead_bin
   worldfile_zero
   surface_flowtable
   subsurface_flowtable
   allometric_table

2. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
   hillslope_rast
   zone_rast
   patch_rast
   stratum_rast
   lai_rast
   
Post conditions
---------------
1. Worldfile with initialized vegetation carbon stores will be saved to the appropriate location of the project directory

2. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   worldfile

Usage:
@code
CreateWorldfile.py -p /path/to/project_dir -c climate_station_name1 ... climate_station_nameN
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
#studyArea = RHESSysMetadata.readStudyAreaEntries(context)
grassMetadata = RHESSysMetadata.readGRASSEntries(context)
if not 'hillslope_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a hillslope raster" % (context.projectDir,)) 
if not 'zone_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a zone raster" % (context.projectDir,)) 
if not 'patch_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a patch raster" % (context.projectDir,)) 
if not 'stratum_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a stratum raster" % (context.projectDir,)) 
if not 'lai_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with an LAI raster" % (context.projectDir,)) 

metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))
if not 'rhessys_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys directory" % (context.projectDir,))
if not 'lairead_bin' in metadata:
    sys.exit("Metadata in project directory %s does not contain a lairead executable" % (context.projectDir,))
if not 'worldfile_zero' in metadata:
    sys.exit("Metadata in project directory %s does not contain an initial worldfile" % (context.projectDir,))
if not 'surface_flowtable' in metadata:
    sys.exit("Metadata in project directory %s does not contain a surface flowtable" % (context.projectDir,))
if not 'subsurface_flowtable' in metadata:
    sys.exit("Metadata in project directory %s does not contain a subsurface flowtable" % (context.projectDir,))
if not 'allometric_table' in metadata:
    sys.exit("Metadata in project directory %s does not contain an allometric table" % (context.projectDir,))

rhessysDir = metadata['rhessys_dir']
paths = RHESSysPaths(args.projectDir, rhessysDir)

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

## 1. Determine legal simulation start and date from climate data 
# Read first climate station from worldfile

# Read climate timeseries for start and end date, write to metadata

## 2. Run LAI read to generate redefine worldfile

## 3. Write TEC file for redefining the initial flow table
##    Redefine on the second day of the simulation, write output
##    on the third day

## 4. Run RHESSys for the first 4 legal days with redefine TEC

## 5. Rename redefine worldfile, write to metadata   