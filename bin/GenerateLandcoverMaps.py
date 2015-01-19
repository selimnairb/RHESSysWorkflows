#!/usr/bin/env python
"""@package GenerateLandcoverMaps

@brief Import landcover raster maps into a GRASS location and generate 
landcover, road and impervious coverage maps.

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
   landcover_rast
   stratum_rast [if defonly==False]
   landuse_rast [if defonly==False]
   
3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   paramdb
   paramdb_dir
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   landcover_road_rule
   landcover_impervious_rule
   landcover_stratum_rule
   landcover_landuse_rule
   landcover_lai_rule [if LAI flag is specified]
   
Post conditions
---------------
1. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   stratum_defs
   landuse_defs
   
2. Will write the following entry(ies) to the GRASS section of metadata associated with the project directory:
   roads_rast [if skiproads == False] [if defonly==True]
   impervious_rast [if defonly==True]
   landuse_rast [if defonly==True]
   stratum_rast [if defonly==True]
   lai_rast [if LAI flag is specified] [if defonly==True]
 
Usage:
@code
GenerateLandcoverMaps.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys, shutil
import argparse
import importlib

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Generate landcover maps in GRASS GIS')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-l', '--makeLaiMap', dest='makeLaiMap', required=False, action='store_true',
                    help='Make LAI map')
parser.add_argument('--skipRoads', dest='skipRoads', required=False, action='store_true', default=False,
                    help='Do not make roads map')
parser.add_argument('--defonly', dest='defonly', required=False, action='store_true',
                    help='Only generate landuse and stratum definition files, do not try to create maps.  Maps must already exist.')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
grassMetadata = RHESSysMetadata.readGRASSEntries(context)
if not 'landcover_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a landcover raster" % (context.projectDir,))
if not 'dem_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a DEM raster in a GRASS mapset" % (context.projectDir,)) 

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

paramDbPath = os.path.join(context.projectDir, metadata['paramdb'])
if not os.access(paramDbPath, os.R_OK):
    sys.exit("Unable to read RHESSys parameters database %s" % (paramDbPath,) )
paramDbPath = os.path.abspath(paramDbPath)

roadRulePath = os.path.join(context.projectDir, metadata['landcover_road_rule'])
if not os.access(roadRulePath, os.R_OK):
    sys.exit("Unable to read rule %s" % (roadRulePath,) )    
imperviousRulePath = os.path.join(context.projectDir, metadata['landcover_impervious_rule'])
if not os.access(imperviousRulePath, os.R_OK):
    sys.exit("Unable to read rule %s" % (imperviousRulePath,) )
landuseRulePath = os.path.join(context.projectDir, metadata['landcover_landuse_rule'])
if not os.access(landuseRulePath, os.R_OK):
    sys.exit("Unable to read rule %s" % (landuseRulePath,) )
stratumRulePath = os.path.join(context.projectDir, metadata['landcover_stratum_rule'])
if not os.access(stratumRulePath, os.R_OK):
    sys.exit("Unable to read rule %s" % (stratumRulePath,) )
laiRulePath = None
if args.makeLaiMap:
    laiRulePath = os.path.join(context.projectDir, metadata['landcover_lai_rule'])
    if not os.access(laiRulePath, os.R_OK):
        sys.exit("Unable to read rule %s" % (laiRulePath,) )

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])

# Import ParamDB from project directory
sys.path.append( os.path.join(context.projectDir, metadata['paramdb_dir']) )
params = importlib.import_module('rhessys.params')
paramConst = importlib.import_module('rhessys.constants')
paramDB = params.paramDB(filename=paramDbPath)

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

landcoverRast = grassMetadata['landcover_rast']
demRast = grassMetadata['dem_rast']

# Make sure mask and region are properly set
result = grassLib.script.run_command('r.mask', flags='r')
if result != 0:
    sys.exit("r.mask filed, returning %s" % (result,) )
result = grassLib.script.run_command('g.region', rast=demRast)
if result != 0:
    sys.exit("g.region failed to set region to DEM, returning %s" % (result,))

# Reclassify landcover into stratum map
stratumRast = 'stratum'
if args.defonly:
    stratumRast = grassMetadata['stratum_rast']
else:
    # Create stratum map
    result = grassLib.script.read_command('r.reclass', input=landcoverRast, output=stratumRast, 
                               rules=stratumRulePath, overwrite=args.overwrite)
    if None == result:
        sys.exit("r.reclass failed to create stratum map, returning %s" % (result,))
    RHESSysMetadata.writeGRASSEntry(context, 'stratum_rast', stratumRast)

# Fetch relevant stratum default files from param DB
pipe = grassLib.script.pipe_command('r.stats', flags='licn', input=stratumRast)
rasterVals = {}
for line in pipe.stdout:
    (dn, cat, num) = line.strip().split()
    if cat != 'NULL':
        rasterVals[cat] = int(dn)
pipe.wait()
print("Writing stratum definition files to %s" % (paths.RHESSYS_DEF) )
for key in rasterVals.keys():
    print("stratum '%s' has dn %d" % (key, rasterVals[key]) )
    paramsFound = paramDB.search(paramConst.SEARCH_TYPE_HIERARCHICAL, None, key, None, None, None, None, None, None, None, None,
                                 defaultIdOverride=rasterVals[key])
    assert(paramsFound)
    paramDB.writeParamFileForClass(paths.RHESSYS_DEF)

# Reclassify landcover into landuse map
landuseRast = 'landuse'
if args.defonly:
    landuseRast = grassMetadata['landuse_rast']
else:
    result = grassLib.script.read_command('r.reclass', input=landcoverRast, output=landuseRast, 
                               rules=landuseRulePath, overwrite=args.overwrite)
    if None == result:
        sys.exit("r.reclass failed to create stratum map, returning %s" % (result,))
    RHESSysMetadata.writeGRASSEntry(context, 'landuse_rast', landuseRast)

# Fetch relevant landuse default files from param DB
pipe = grassLib.script.pipe_command('r.stats', flags='licn', input=landuseRast)
rasterVals = {}
for line in pipe.stdout:
    (dn, cat, num) = line.strip().split()
    if cat != 'NULL':
        rasterVals[cat] = int(dn)
pipe.wait()
print("Writing landuse definition files to %s" % (paths.RHESSYS_DEF) )
for key in rasterVals.keys():
    print("landuse '%s' has dn %d" % (key, rasterVals[key]) )
    paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, key, None, None, None, None, None, None, None, None,
                                 limitToBaseClasses=True, defaultIdOverride=rasterVals[key])
    assert(paramsFound)
    paramDB.writeParamFileForClass(paths.RHESSYS_DEF)

# Reclassify landcover into road map
if not args.skipRoads and (not args.defonly):
    result = grassLib.script.read_command('r.reclass', input=landcoverRast, output='roads', 
                               rules=roadRulePath, overwrite=args.overwrite)
    if None == result:
        sys.exit("r.reclass failed to create roads map, returning %s" % (result,))
    RHESSysMetadata.writeGRASSEntry(context, 'roads_rast', 'roads')    

# Reclassify landcover into impervious map
if not args.defonly:
    result = grassLib.script.read_command('r.reclass', input=landcoverRast, output='impervious', 
                               rules=imperviousRulePath, overwrite=args.overwrite)
    if None == result:
        sys.exit("r.reclass failed to create impervious map, returning %s" % (result,))
    RHESSysMetadata.writeGRASSEntry(context, 'impervious_rast', 'impervious')    

# Reclassify landcover into LAI map
if args.makeLaiMap and (not args.defonly):
    if RHESSysMetadata.LC_RULE_LAI_COMPAT == os.path.basename(metadata['landcover_lai_rule']):
        # Compatibility mode, use r.reclass
        result = grassLib.script.read_command('r.reclass', input=landcoverRast, output='lai', 
                                              rules=laiRulePath, overwrite=args.overwrite)
        if None == result:
            sys.exit("r.reclass failed to create LAI map, returning %s" % (result,))
    else:
        # use r.reclass
        result = grassLib.script.read_command('r.recode', input=landcoverRast, output='lai', 
                                              rules=laiRulePath, overwrite=args.overwrite)
        if None == result:
            sys.exit("r.reclass failed to create LAI map, returning %s" % (result,))
        
    RHESSysMetadata.writeGRASSEntry(context, 'lai_rast', 'lai') 

# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'stratum_defs', True)
RHESSysMetadata.writeRHESSysEntry(context, 'landuse_defs', True)

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)