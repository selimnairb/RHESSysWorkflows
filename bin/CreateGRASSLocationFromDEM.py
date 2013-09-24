#!/usr/bin/env python
"""@package CreateGRASSLocationFromDEM

@brief Import DEM into new GRASS GIS location

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
   'GRASS', 'MODULE_PATH'

2. The following metadata entry(ies) must be present in the manifest section of the metadata associated with the project directory:
   dem

3. The following metadata entry(ies) must be present in the study area section of the metadata associated with the project directory:
   dem_srs

Post conditions
---------------
1. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   model_description

2. GRASS location and mapset will be created in grass_dbase

3. Will write the following entry(ies) to the GRASS section of metadata associated with the project directory:
   dem_rast

Usage:
@code
CreateGRASSLocationFromDEM.py -p /path/to/project_dir -script GRASSData -l default -m "Grass location for RHESSys model of Dead Run watershed in Baltimore, MD"
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import sys
import argparse
import re

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Import spatial data needed to create RHESSys worldfile into the PERMANENT mapset of a new GRASS location')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-g', '--grassDbase', dest='grassDbase', required=False,
                    help='Path within project directory of the GRASS database where the new location is to be created.')
parser.add_argument('-l', '--location', dest='location', required=False,
                    help='Name of the new GRASS location where study area data are to be imported.')
parser.add_argument('-m', '--mapset', dest='mapset', required=False,
                    help='Name of the new GRASS mapset where study area data are to be imported.')
parser.add_argument('-d', '--description', dest='description', required=True,
                    help='Description for new location')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 
paths = RHESSysPaths(args.projectDir)

if not args.grassDbase:
    dbase = 'GRASSData'
else:
    dbase = args.grassDbase
grassDbase = os.path.join(context.projectDir, dbase)
location = None
if args.location:
    location = args.location
mapset = None
if args.mapset:
    mapset = args.mapset

# Check for necessary information in metadata
manifest = RHESSysMetadata.readManifestEntries(context)
if not 'dem' in manifest:
    sys.exit("Metadata in project directory %s does not contain a DEM reference" % (context.projectDir,)) 

studyArea = RHESSysMetadata.readStudyAreaEntries(context)
if not 'dem_srs' in studyArea:
    sys.exit("Metadata in project directory %s does not contain DEM spatial reference" % (context.projectDir,)) 
srsPattern = re.compile('EPSG:(\d+)')
result = srsPattern.search(studyArea['dem_srs'])
if not result:
    sys.exit("Spatial reference must be specified in the form 'EPSG:<number>'")
srs = int(result.group(1))

# Set up GRASS environment
grassConfig = GRASSConfig(context, grassDbase, location, mapset, newLocation=True, overwrite=args.overwrite)
grassLib = GRASSLib(grassConfig=grassConfig)

# Create the new location
grassLib.script.core.create_location(grassConfig.dbase, grassConfig.location, epsg=srs, desc=args.description)

# Import DEM into location
demFilepath = os.path.join(context.projectDir, manifest['dem'])
#print demFilepath
result = grassLib.script.run_command('r.in.gdal', flags="e", input=demFilepath, output='dem')
if result != 0:
    sys.exit("Failed to import DEM into new GRASS dataset %s/%s, results:\n%s" % \
             (grassDbase, args.location, result) )

# Set region to DEM
result = grassLib.script.run_command('g.region', rast='dem')
if result != 0:
    sys.exit("Failed to set region to DEM")

# Update metadata
RHESSysMetadata.writeGRASSEntry(context, 'dem_rast', 'dem')
RHESSysMetadata.writeRHESSysEntry(context, 'grass_dbase', dbase)
RHESSysMetadata.writeRHESSysEntry(context, 'grass_location', grassConfig.location)
RHESSysMetadata.writeRHESSysEntry(context, 'grass_mapset', grassConfig.mapset)
RHESSysMetadata.writeRHESSysEntry(context, 'rhessys_dir', paths.rhessysDir)
RHESSysMetadata.writeRHESSysEntry(context, 'model_description', args.description)

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)