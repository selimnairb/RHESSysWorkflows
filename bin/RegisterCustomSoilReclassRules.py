#!/usr/bin/env python
"""@package GenerateSoilTextureMap

@brief Query RHESSys ParamDB for soil definitions for a custom soil map.  

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

2. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
   dem_rast
   soil_rast

3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   paramdb
   paramdb_dir
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir

Post conditions
---------------
1. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   soil_rule
   
Usage:
@code
GenerateCustomSoilDefinitions.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys, errno
import argparse
import textwrap

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Generate soil texture map for dataset in GRASS GIS')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-b', '--buildPrototypeRules', dest='buildPrototypeRules', required=False, action='store_true',
                    help='Write prototype soil reclass rules to the project directory. You must edit these rules to match the classes in your custom soils data')
group.add_argument('-r', '--ruleDir', dest='ruleDir', required=False,
                    help="The directory where soils reclass rule can be found; must contain the file %s" % (str(RHESSysMetadata.SOILS_RULES),) )
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))
if not 'paramdb_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a ParamDB directory" % (context.projectDir,))
if not 'paramdb' in metadata:
    sys.exit("Metadata in project directory %s does not contain a ParamDB" % (context.projectDir,))

grassMetadata = RHESSysMetadata.readGRASSEntries(context)
if not 'dem_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a DEM raster in a GRASS mapset" % (context.projectDir,)) 
demRast = grassMetadata['dem_rast']
if not 'soil_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a soil raster in a GRASS mapset" % (context.projectDir,)) 
soilRast = grassMetadata['soil_rast']

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])

# Write prototype soil reclass rules to the project directory
if args.buildPrototypeRules:
    sys.stdout.write('Generating prototype soil reclass rules...')
    sys.stdout.flush()
    # Get path of place to store reclass rules
    projectDirRuleDir = paths.getReclassRulesDirectory()
    soilsRulePath = os.path.join(projectDirRuleDir, RHESSysMetadata.SOILS_RULE)
    with open(soilsRulePath, 'w') as f:
        f.write('1 = 1 clay\n')
        f.write('2 = 2 silt-clay\n')
        f.write('3 = 3 silt-clay-loam\n')
        f.write('4 = 4 sandy-clay\n')
        f.write('5 = 5 sandy-clay-loam\n')
        f.write('6 = 6 clay-loam\n')
        f.write('7 = 7 silt\n')
        f.write('8 = 8 silt-loam\n')
        f.write('9 = 9 loam\n')
        f.write('10 = 10 sand\n')
        f.write('11 = 11 loamy-sand\n')
        f.write('12 = 12 sandy-loam\n')
        f.write('13 = 13 rock\n')
        f.write('14 = 14 water\n')
    ruleDir = None
    sys.stdout.write('done\n')
    

# Import rules from elsewhere
if args.ruleDir:
    if not os.access(args.ruleDir, os.R_OK):
        sys.exit("Unable to read rule directory %s" % (ruleDir,) )
    ruleDir = os.path.abspath(args.ruleDir)

if ruleDir:
    sys.stdout.write(textwrap.fill("Importing soil reclass rules from %s ..." % (ruleDir,) ) )
    sys.stdout.flush()
    # Copy rules into project directory
    soilsRulePath = os.path.join(ruleDir, RHESSysMetadata.SOILS_RULE)
    shutil.copy(soilsRulePath, projectDirRuleDir)
    sys.stdout.write('done\n')
    
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'soil_rule', os.path.join(RHESSysMetadata.RULES_DIR, os.path.basename(soilsRulePath)) )

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)