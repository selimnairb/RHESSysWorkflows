#!/usr/bin/env python
"""@package GenerateSoilTextureMap

@brief Import percent sand and percent clay raster maps into a GRASS location
and generate soil texture map using r.soils.texture. 

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
   soil_raster_pctsand [if defonly==False]
   soil_raster_pctclay [if defonly==False]

3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   paramdb
   paramdb_dir
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   
4. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
   dem_rast
   soil_rast [if defonly==True]
   
5. Requires r.soils.texture GRASS extension: http://grasswiki.osgeo.org/wiki/GRASS_AddOns#r.soils.texture

Post conditions
---------------
1. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   soil_defs
   
2. Will write the following entry(ies) to the GRASS section of metadata associated with the project directory:
   soil_avgsand_rast [if defonly==False]
   soil_avgclay_rast [if defonly==False]
   soil_rast [if defonly==False]
   
Usage:
@code
GenerateSoilTextureMap.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys, errno
import argparse

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
parser.add_argument('--defonly', dest='defonly', required=False, action='store_true',
                    help='Only generate soil definition files, do not try to create soil texture map.  Map must already exist.')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

soil_rast = 'soil_texture'

# Check for necessary information in metadata
manifest = RHESSysMetadata.readManifestEntries(context)
if not args.defonly:
    if not 'soil_raster_pctsand' in manifest:
        sys.exit("Metadata in project directory %s does not contain a soil_raster_pctsand raster" % (context.projectDir,))
    if not 'soil_raster_pctclay' in manifest:
        sys.exit("Metadata in project directory %s does not contain a soil_raster_pctclay raster" % (context.projectDir,))

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
if args.defonly:
    if not 'soil_rast' in grassMetadata:
        sys.exit("Metadata in project directory %s does not contain a soil raster in a GRASS mapset" % (context.projectDir,))
    soil_rast = grassMetadata['soil_rast'] 

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])

# Import ParamDB from project directory
paramDbPath = os.path.join(context.projectDir, metadata['paramdb'])
if not os.access(paramDbPath, os.R_OK):
    sys.exit("Unable to read RHESSys parameters database %s" % (paramDbPath,) )
sys.path.append( os.path.join(context.projectDir, metadata['paramdb_dir']) )
params = importlib.import_module('rhessys.params')
paramConst = importlib.import_module('rhessys.constants')
paramDB = params.paramDB(filename=paramDbPath)

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
moduleEtc = context.config.get('GRASS', 'MODULE_ETC')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

# Make sure mask and region are properly set
result = grassLib.script.run_command('r.mask', flags='r')
if result != 0:
    sys.exit("r.mask filed, returning %s" % (result,) )
result = grassLib.script.run_command('g.region', rast=demRast)
if result != 0:
    sys.exit("g.region failed to set region to DEM, returning %s" % (result,))

if not args.defonly:
    sys.stdout.write('Generating soil texture map from percent sand and clay maps...')
    sys.stdout.flush()
    # Import percent sand and percent clay raster maps into GRASS
    percentSandRasterPath = os.path.join(context.projectDir, manifest['soil_raster_pctsand'])
    result = grassLib.script.run_command('r.in.gdal', input=percentSandRasterPath, output='soil_pctsand', overwrite=args.overwrite)
    if result != 0:
        sys.exit("Failed to import soil_raster_pctsand into GRASS dataset %s/%s, results:\n%s" % \
                 (grassDbase, metadata['grass_location'], result) )
    RHESSysMetadata.writeGRASSEntry(context, 'soil_pctsand_rast', 'soil_pctsand')
        
    percentClayRasterPath = os.path.join(context.projectDir, manifest['soil_raster_pctclay'])
    result = grassLib.script.run_command('r.in.gdal', input=percentClayRasterPath, output='soil_pctclay', overwrite=args.overwrite)
    if result != 0:
        sys.exit("Failed to import soil_raster_pctclay into GRASS dataset %s/%s, results:\n%s" % \
                 (grassDbase, metadata['grass_location'], result) )
    RHESSysMetadata.writeGRASSEntry(context, 'soil_pctclay_rast', 'soil_pctclay')
    
    # Generate soil texture map
    schemePath = os.path.join(moduleEtc, 'USDA.dat')
    if not os.access(schemePath, os.R_OK):
        raise IOError(errno.EACCES, "Not allowed to read r.soils.texture scheme %s" % (schemePath,) )
    soilTexture = os.path.join(modulePath, 'r.soils.texture')
    result = grassLib.script.read_command(soilTexture, sand='soil_pctsand', clay='soil_pctclay',
                                          scheme=schemePath, output=soil_rast, overwrite=args.overwrite)
    if None == result:
        sys.exit("r.soils.texture failed, returning %s" % (result,))
    RHESSysMetadata.writeGRASSEntry(context, 'soil_rast', soil_rast)
    
    sys.stdout.write('done\n')

sys.stdout.write('Reading soil parameter definitions from RHESSys ParamDB...')
sys.stdout.flush()

# Fetch relevant soil default files from param DB
pipe = grassLib.script.pipe_command('r.stats', flags='licn', input=soil_rast)
textures = {}
for line in pipe.stdout:
    (dn, cat, num, ) = line.strip().split()
    if cat != 'NULL':
        textures[cat] = int(dn)
pipe.wait()
print("Writing soil definition files to %s" % (paths.RHESSYS_DEF) )
for key in textures.keys():
    print("soil '%s' has dn %d" % (key, textures[key]) )
    paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, key, None, None, None, None, None, None, None, None,
                                 limitToBaseClasses=True, defaultIdOverride=textures[key])
    assert(paramsFound)
    paramDB.writeParamFileForClass(paths.RHESSYS_DEF)

# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'soil_defs', True)

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)
