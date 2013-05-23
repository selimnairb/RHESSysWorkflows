#!/usr/bin/env python
"""@package GenerateLandcoverMaps

@brief Import landcover raster maps into a GRASS location and generate 
landcover, lai, and impervious coverage maps.

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
   'SCRIPT', 'ETC'

2. The following metadata entry(ies) must be present in the manifest section of the metadata associated with the project directory:
   landcover
   
3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   
4. The following metadata entry(ies) must be present in the study area section of the metadata associated with the project directory:
   landcover_type
   
Post conditions
---------------
1. The following raster datasets will be created in the GRASS location:
   landcover_raw
   landcover
   impervious
   lai

2. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   lancover_rule
   landcover_impervious_rule
   landcover_lai_rule

Usage:
@code
GenerateLandcoverMaps.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 

@todo separate out LAI: use NASA NEX min and max LAI, then run RHESSys lairead after worldfile is built (eventually we will roll lairead into g2w)
"""
import os, sys, errno, shutil
import argparse
import ConfigParser

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata

KNOWN_LC_TYPES = ['NLCD2006']

# Handle command line options
parser = argparse.ArgumentParser(description='Generate landcover maps in GRASS GIS')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-r', '--ruleDir', dest='ruleDir', required=False,
                    help='The directory where landcover reclass rules can be found')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
studyArea = RHESSysMetadata.readStudyAreaEntries(context)
landcoverType = studyArea['landcover_type']

if landcoverType in KNOWN_LC_TYPES:
    if args.ruleDir:
        ruleDir = os.path.abspath(args.ruleDir)
    else:
        scriptEtc = context.config.get('SCRIPT', 'ETC')
        ruleDir = os.path.join(scriptEtc, landcoverType)
else:
    if args.ruleDir:
        ruleDir = os.path.abspath(args.ruleDir)
    else:
        sys.exit("Landcover type %s specified, but land cover conversion rule directory not specified")
    
landcoverRulePath = os.path.join(ruleDir, 'landcover.rule')
if not os.access(landcoverRulePath, os.R_OK):
    sys.exit("Unable to read %s" % (landcoverRulePath,) )
imperviousRulePath = os.path.join(ruleDir, 'impervious.rule')
if not os.access(imperviousRulePath, os.R_OK):
    sys.exit("Unable to read %s" % (imperviousRulePath,) )
laiRulePath = os.path.join(ruleDir, 'lai.rule')
if not os.access(laiRulePath, os.R_OK):
    sys.exit("Unable to read %s" % (laiRulePath,) )

# Check for necessary information in metadata
manifest = RHESSysMetadata.readManifestEntries(context)
if not 'landcover' in manifest:
    sys.exit("Metadata in project directory %s does not contain a landcover raster" % (context.projectDir,))

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

# Import landcover raster map into GRASS
landcoverRasterPath = os.path.join(context.projectDir, manifest['landcover'])
result = grassLib.script.run_command('r.in.gdal', input=landcoverRasterPath, output='landcover_raw', overwrite=args.overwrite)
if result != 0:
    sys.exit("Failed to import landcover into GRASS dataset %s/%s, results:\n%s" % \
             (grassDbase, metadata['grass_location'], result) )

# Reclassify raw landcover into "RHESSys" landcover types
result = grassLib.script.read_command('r.reclass', input='landcover_raw', output='landcover', 
                           rules=landcoverRulePath, overwrite=args.overwrite)
if None == result:
    sys.exit("r.reclass failed to create landcover map, returning %s" % (result,))

# Reclassify landcover into impervious map
result = grassLib.script.read_command('r.reclass', input='landcover', output='impervious', 
                           rules=imperviousRulePath, overwrite=args.overwrite)
if None == result:
    sys.exit("r.reclass failed to create impervious map, returning %s" % (result,))
    
# Reclassify landcover into lai map
result = grassLib.script.read_command('r.reclass', input='landcover', output='lai', 
                           rules=laiRulePath, overwrite=args.overwrite)
if None == result:
    sys.exit("r.reclass failed to create LAI map, returning %s" % (result,))

# Copy rules used to into project directory
shutil.copy(landcoverRulePath, context.projectDir)
shutil.copy(imperviousRulePath, context.projectDir)
shutil.copy(laiRulePath, context.projectDir)
    
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, "lancover_rule", os.path.basename(landcoverRulePath))
RHESSysMetadata.writeRHESSysEntry(context, "landcover_impervious_rule", os.path.basename(imperviousRulePath))
RHESSysMetadata.writeRHESSysEntry(context, "landcover_lai_rule", os.path.basename(laiRulePath))

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)