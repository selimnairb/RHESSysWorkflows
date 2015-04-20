#!/usr/bin/env python
"""@package CreateWorldfile

@brief Generate world template to be used to create an initial worldfile 
for a RHESSys model.

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
1. The following metadata entry(ies) must be present in the study area section of the metadata associated with the project directory: 
   bbox_wgs84

2. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   stratum_defs
   landuse_defs
   soil_defs
   paramdb
   paramdb_dir
   rhessys_dir
   climate_stations
   template_template

3. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
   basin_rast
   dem_rast
   hillslope_rast
   slope_rast
   aspect_rast
   zero_rast
   east_horizon_rast
   west_horizon_rast
   patch_rast
   soil_rast
   landuse_rast
   impervious_rast
   wetness_index_rast 
   stratum_rast
   xmap_rast
   ymap_rast
   
4. The following metadata entry(ies) will be used if present in the GRASS section of the metadata associated with the project directory:
   isohyet_rast
   basestation_rast
   
Post conditions
---------------
1. Template will be created in the RHESSys folder of the project directory.

2. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   template

Usage:
@code
GenerateWorldTemplate.py -p /path/to/project_dir -c climate_station_name1 ... climate_station_nameN
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys
import importlib
import string
import re
import argparse
import textwrap

from oset import oset

from ecohydrolib.grasslib import *
from ecohydrolib.spatialdata.utils import bboxFromString
from ecohydrolib.spatialdata.utils import calculateBoundingBoxCenter

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.rhessys import readParameterFile

# Handle command line options
parser = argparse.ArgumentParser(description='Create RHESSys world template used to create initial world file')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-c', '--climateStation', dest='climateStation', required=False,
                     help='The climate station to associate with the worldfile.  Must be one of the climate stations specified in the "climate_stations" key in the "rhessys" section of the metadata')
parser.add_argument('--aspectMinSlopeOne', dest='aspectMinSlopeOne', action='store_true', required=False,
                    help='Use slope map with a minimum value of 1.0 to be used for calculating spherical average aspect.  Needed for areas of low slope due to limitations of RHESSys grass2world, which truncates slopes <1 to 0.0, which causes spherical average of aspect to equal NaN.')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='Print detailed information about what the program is doing')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
studyArea = RHESSysMetadata.readStudyAreaEntries(context)
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
if not 'stratum_defs' in metadata:
    sys.exit("Metadata in project directory %s does not contain stratum definitions" % (context.projectDir,)) 
if not 'landuse_defs' in metadata:
    sys.exit("Metadata in project directory %s does not contain land use definitions" % (context.projectDir,)) 
if not 'soil_defs' in metadata:
    sys.exit("Metadata in project directory %s does not contain soil definitions" % (context.projectDir,)) 
if not 'rhessys_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys directory" % (context.projectDir,))
if not 'climate_stations' in metadata:
    sys.exit("Metadata in project directory %s does not contain a list of climate stations" % (context.projectDir,))
if not 'template_template' in metadata:
    sys.exit("Metadata in project directory %s does not contain a template template" % (context.projectDir,))
if not 'paramdb_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a ParamDB directory" % (context.projectDir,))
if not 'paramdb' in metadata:
    sys.exit("Metadata in project directory %s does not contain a ParamDB" % (context.projectDir,))

if not args.climateStation and not 'basestations_rast' in grassMetadata:
    sys.exit("You must specify the climate station command line argument of generate a climate base station map")

climateStations = metadata['climate_stations'].split(RHESSysMetadata.VALUE_DELIM)
if args.climateStation and ( not args.climateStation in climateStations ):
    sys.exit("The chosen climate station '%s' was not found in the climate station list in metadata (%s)" %
             (str(args.climateStation), str(metadata['climate_stations']) ) )

rhessysDir = metadata['rhessys_dir']
paths = RHESSysPaths(args.projectDir, rhessysDir)

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
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

# Make sure mask and region are properly set
demRast = grassMetadata['dem_rast']
result = grassLib.script.run_command('g.region', rast=demRast)
if result != 0:
    sys.exit("g.region failed to set region to DEM, returning %s" % (result,))

# Make integer representation of DEM
dem1000Rast = "%s_1000" % (demRast,)
result = grassLib.script.write_command('r.mapcalc',
                                       stdin="%s=%s * 1000" % (dem1000Rast, demRast) )
if result != 0:
    sys.exit("r.mapcalc failed to integer DEM, returning %s" % (result,))

basinRast = grassMetadata['basin_rast']
result = grassLib.script.run_command('r.mask', flags='o', input=basinRast, maskcats='1')
if result != 0:
    sys.exit("r.mask failed to set mask to basin, returning %s" % (result,))

bbox = bboxFromString(studyArea['bbox_wgs84'])
(longitude, latitude) = calculateBoundingBoxCenter(bbox)

## 1. Get default files for basin, hillslope, and zone from default database
sys.stdout.write('Getting parameter definition files for basin, hillslope, and zone...')
sys.stdout.flush()
paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, 'basin', None, None, None, None, None, None, None, None,
                             limitToBaseClasses=False, defaultIdOverride=str(1))
assert(paramsFound)
paramDB.writeParamFileForClass(paths.RHESSYS_DEF)
paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, 'hillslope', None, None, None, None, None, None, None, None,
                             limitToBaseClasses=False, defaultIdOverride=str(1))
assert(paramsFound)
paramDB.writeParamFileForClass(paths.RHESSYS_DEF)
paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, 'zone', None, None, None, None, None, None, None, None,
                             limitToBaseClasses=False, defaultIdOverride=str(1))
assert(paramsFound)
paramDB.writeParamFileForClass(paths.RHESSYS_DEF)
sys.stdout.write('done\n')

## 2. Determine the number of definition files of each type and save their names for inclusion in the world file
sys.stdout.write("\nFinding definition files in %s..." % (paths.RHESSYS_DEF,) )
sys.stdout.flush()
defFiles = {}
contents = os.listdir(paths.RHESSYS_DEF)
for type in paramConst.VALID_TYPES:
    if args.verbose:
        print("Definition files found for type: %s" % (type, ) )
    typeRe = re.compile("^%s_.+\.def$" % (type,) )
    if defFiles.has_key(type):
        defs = defFiles[type]
    else:
        defs = []
        defFiles[type] = defs
    for entry in contents:
        m = typeRe.match(entry)
        if m:
            if args.verbose:
                print("\t%s" % entry)
            defFiles[type].append(entry)

# Make sure there are soil, landuse and stratum defaults
if not defFiles.has_key('soil') or len(defFiles['soil']) < 1:
    sys.exit("No soil definition files found")
if not defFiles.has_key('landuse') or len(defFiles['landuse']) < 1:
    sys.exit("No land use definition files found")
if not defFiles.has_key('stratum') or len(defFiles['stratum']) < 1:
    sys.exit("No stratum definition files found")

sys.stdout.write('done\n')

## 3. Open worldfile template template and substitute values
templateTemplatePath = os.path.join(context.projectDir, metadata['template_template'])
sys.stdout.write("\nGenerating template from template template %s..." % (templateTemplatePath,) )
sys.stdout.flush()

templateTemplateFile = open(templateTemplatePath)
templateTemplate = string.Template(templateTemplateFile.read())
templateTemplateFile.close()
# Our dictionary of substitutions
subs = {}

# First, build substitution dictionary for default files
defs = None
for key in defFiles.keys():
    defs = defFiles[key]
    numDefin = len(defs)
    if numDefin >= 1:
        numDefinKey = "num_%s_defs" % (key,)    
        if args.verbose:
            print("%s: %d" % (numDefinKey, numDefin) )
        subs[numDefinKey] = str(numDefin)
    
        defStr = os.path.join(paths._DEF, defs[0])
        for defin in defs[1:]:
            defStr += os.linesep + os.path.join(paths._DEF, defin)
        defStrKey = "%s_defs" % (key,)
        if args.verbose:
            print("%s: %s" % (defStrKey, defStr) )
        subs[defStrKey] = defStr

# Second, climate stations
if args.climateStation:
    # Use the base station specified on command line
    if args.verbose:
        print("Using single climate station: %s" % (args.climateStation,) )
    climParamFilename = "%s.base" % (args.climateStation,)
    baseFile = os.path.join(paths._CLIM, climParamFilename)
    subs['climate_stations'] = baseFile
    subs['num_climate_stations'] = 1

    climParams = readParameterFile( os.path.join(paths.RHESSYS_CLIM, climParamFilename) )
    climateStationIDStr = "base_station_ID\tdvalue %s" % (climParams['base_station_id'],)
    subs['zone_base_station_ids'] = climateStationIDStr
    subs['zone_num_base_stations'] = 1
else:
    # Use base station raster map
    if args.verbose:
        print("Reading climate stations from raster: %s" % (grassMetadata['basestations_rast'],) )
    # Get list of base station IDs from raster
    rasterIds = oset()
    pipe = grassLib.script.pipe_command('r.stats', flags='licn', input=grassMetadata['basestations_rast'])
    for line in pipe.stdout:
        values = line.strip().split()
        if values[1] != 'NULL':
            rasterIds.add( int(values[0]) )
    # Get base station IDs from base station files
    baseIds = oset()
    baseFiles = {}
    for station in metadata['climate_stations'].split(','):
        climParamFilename = "%s.base" % (station,)
        baseFile = os.path.join( paths._CLIM, climParamFilename )
        climParams = readParameterFile( os.path.join(paths.RHESSYS_CLIM, climParamFilename) )
        id = int(climParams['base_station_id'])
        baseIds.add(id)
        baseFiles[id] = baseFile
    
    includedBaseIds = rasterIds & baseIds
    
    if len(includedBaseIds) == 0:
        sys.exit( textwrap.fill( "Some climate base station raster values do not have corresponding base station files. Raster values: %s, base station IDs: %s" % \
                                 (str(rasterIds), str(baseIds) ) ) )
    
    climateStationsStr = baseFiles[includedBaseIds[0]]
    for id in includedBaseIds[1:]:
        climateStationsStr += os.linesep + baseFiles[id]
    subs['climate_stations'] = climateStationsStr
    subs['num_climate_stations'] = len(includedBaseIds)
    
    climateStationIDStr = "base_station_ID\tmode %s" % (grassMetadata['basestations_rast'],)
    subs['zone_base_station_ids'] = climateStationIDStr
    subs['zone_num_base_stations'] = 1

# B. Everything else
subs['world_rast'] = grassMetadata['basin_rast']
subs['basin_rast'] = grassMetadata['basin_rast']
subs['dem_rast'] = dem1000Rast
subs['latitude_float'] = str(latitude)
subs['hillslope_rast'] = grassMetadata['hillslope_rast']
subs['zone_rast'] = grassMetadata['zone_rast']
subs['slope_rast'] = grassMetadata['slope_rast']
subs['aspect_rast'] = grassMetadata['aspect_rast']
if args.aspectMinSlopeOne:
    # Use minimum slope of 1 for calculating spherical average of aspect
    result = grassLib.script.write_command('r.mapcalc', stdin='slopegte1=if(slope<1,1,slope)')
    if result != 0:
        sys.exit("r.mapcalc failed to create slope >= 1 map, returning %s" % (result,))
    subs['aspect_slope_rast'] = 'slopegte1'
else:
    subs['aspect_slope_rast'] = grassMetadata['slope_rast']

if 'isohyet_rast' in grassMetadata:
    isohyet = grassMetadata['isohyet_rast']
    # Scale isohyet by 100 to avoid integer truncation by grass2world
    isohyet100 = isohyet + '100'
    result = grassLib.script.write_command('r.mapcalc', 
                                           stdin="{isohyet100} = {isohyet} * 100".format(isohyet100=isohyet100,
                                                                                         isohyet=isohyet))
    if result != 0:
        sys.exit("r.mapcalc failed to create %s map, returning %s" % (isohyet100, result))
    subs['isohyet_rast'] = isohyet100
else:
    result = grassLib.script.write_command('r.mapcalc', stdin='onehundred=100')
    if result != 0:
        sys.exit("r.mapcalc failed to create onehundred map, returning %s" % (result,))
    subs['isohyet_rast'] = 'onehundred'
subs['east_horizon_rast'] = grassMetadata['east_horizon_rast']
subs['west_horizon_rast'] = grassMetadata['west_horizon_rast']
subs['patch_rast'] = grassMetadata['patch_rast']
subs['soil_rast'] = grassMetadata['soil_rast']
subs['landuse_rast'] = grassMetadata['landuse_rast']
subs['impervious_rast'] = grassMetadata['impervious_rast']
subs['wetness_index_rast'] = grassMetadata['wetness_index_rast'] 
subs['stratum_rast'] = grassMetadata['stratum_rast']
subs['xmap_rast'] = grassMetadata['xmap_rast']
subs['ymap_rast'] = grassMetadata['ymap_rast']

# Third, substitute into the template template, producing the template, which we write to disk for g2w
templateStr = ''
try:
    templateStr = templateTemplate.substitute(subs)
    if args.verbose:
        print("Template:")
        print(templateStr)
except KeyError as e:
    sys.exit("ERROR creating worldfile template: template variable %s was not specified" % (str(e),) )
except ValueError:
    sys.exit("A '$' character was found in the template template, which is illegal")

# Write the template to a file stored in paths.RHESSYS_TEMPLATES, using the filename
# of the template template as a basis
templateFilename = os.path.splitext( os.path.split( metadata['template_template'] )[1] )[0]
templateFilepath = os.path.join(paths.RHESSYS_TEMPLATES, templateFilename)
f = open(templateFilepath, 'w')
f.write(templateStr)
f.close()
RHESSysMetadata.writeRHESSysEntry(context, 'template', paths.relpath(templateFilepath) )

sys.stdout.write('done\n')

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)