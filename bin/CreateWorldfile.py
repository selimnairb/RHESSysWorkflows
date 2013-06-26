#!/usr/bin/env python
"""@package CreateWorldfile

@brief Create RHESSys worldfile.

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
   'RHESSYS', 'PATH_OF_PARAMDB'

2. The following metadata entry(ies) must be present in the study area section of the metadata associated with the project directory: 
   bbox_wgs84

3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   g2w_bin
   rat_bin
   climate_stations
   template_template

4. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
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
   wetness_index_rast 
   stratum_rast
   
Post conditions
---------------
1. Template and worldfile will be created in the RHESSys folder of the project directory.

2. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   template
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

from rhessys.params import paramDB
import rhessys.constants as paramConst

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
parser.add_argument('-c', '--climateStations', dest='climateStations', required=True, nargs='+',
                     help='The climate station(s) to associate with the worldfile.  Must be one of the climate stations specified in the "climate_stations" key in the "rhessys" section of the metadata')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='Print detailed information about what the program is doing')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

paramDbPath = context.config.get('RHESSYS', 'PATH_OF_PARAMDB')
if not os.access(paramDbPath, os.R_OK):
    sys.exit("Unable to read RHESSys parameters database %s" % (paramDbPath,) )
paramDbPath = os.path.abspath(paramDbPath)

# Check for necessary information in metadata
studyArea = RHESSysMetadata.readStudyAreaEntries(context)
grassMetadata = RHESSysMetadata.readGRASSEntries(context)
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
if not 'climate_stations' in metadata:
    sys.exit("Metadata in project directory %s does not contain a list of climate stations" % (context.projectDir,))
if not 'template_template' in metadata:
    sys.exit("Metadata in project directory %s does not contain a template template" % (context.projectDir,))

if not args.climateStations <= metadata['climate_stations']:
    sys.exit("Some of the chosen climate stations (%s) were not found in the climate station list in metadata (%s)" %
             (str(args.climateStations), str(metadata['climate_stations']) ) )

bbox = bboxFromString(studyArea['bbox_wgs84'])
(longitude, latitude) = calculateBoundingBoxCenter(bbox)

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])
paramDB = paramDB(filename=paramDbPath)

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

## 1. Get default files for basin, hillslope, and zone from default database
sys.stdout.write('Getting parameter definitions files for basin, hillslope, and zone...')
sys.stdout.flush()
paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, 'basin', None, None, None, None, None, None, None, None)
assert(paramsFound)
paramDB.writeParamFiles(paths.RHESSYS_DEF)
paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, 'hillslope', None, None, None, None, None, None, None, None)
assert(paramsFound)
paramDB.writeParamFiles(paths.RHESSYS_DEF)
paramsFound = paramDB.search(paramConst.SEARCH_TYPE_CONSTRAINED, None, 'zone', None, None, None, None, None, None, None, None)
assert(paramsFound)
paramDB.writeParamFiles(paths.RHESSYS_DEF)
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
    
        defStr = os.path.join('..', paths._DEF, defs[0])
        for defin in defs[1:]:
            defStr += os.linesep + os.path.join('..', paths._DEF, defin)
        defStrKey = "%s_defs" % (key,)
        if args.verbose:
            print("%s: %s" % (defStrKey, defStr) )
        subs[defStrKey] = defStr
        
# Second, a climate stations and raster layers to substitution dictionary
# A. Climate stations
numClimateStations = len(args.climateStations)
if args.verbose:
    print("%s: %d" % ('num_climate_stations', numClimateStations) )
subs['num_climate_stations'] = str(numClimateStations)
subs['zone_num_base_stations'] = str(numClimateStations)

# The first climate stations
climParamFilename = "%s.base" % (args.climateStations[0],)
climateStationsStr = os.path.join('..', paths._CLIM, climParamFilename)
climParams = readParameterFile(os.path.join(paths.RHESSYS_CLIM, climParamFilename))
climateStationIDStr = "base_station_ID\tdvalue %s" % (climParams['base_station_id'], )
# The rest of the climate stations
for clim in args.climateStations[1:]:
    climParamFilename = "%s.base" % (clim,)
    climateStationsStr += os.linesep + os.path.join('..', paths._CLIM, climParamFilename)
    climParams = readParameterFile(os.path.join(paths.RHESSYS_CLIM, climParamFilename))
    climateStationIDStr += "%sbase_station_ID\tdvalue %s" % (os.linesep, climParams['base_station_id'], )
climateStationsKey = 'climate_stations'
if args.verbose:
    print("%s: %s" % (climateStationsKey, climateStationsStr) )
subs[climateStationsKey] = climateStationsStr
if args.verbose:
    print("%s: %s" % ('zone_base_station_ids', climateStationIDStr) )
subs['zone_base_station_ids'] = climateStationIDStr

# B. Everything else
subs['world_rast'] = grassMetadata['basin_rast']
subs['basin_rast'] = grassMetadata['basin_rast']
subs['dem_rast'] = grassMetadata['dem_rast']
subs['latitude_float'] = str(latitude)
subs['hillslope_rast'] = grassMetadata['hillslope_rast']
subs['zone_rast'] = grassMetadata['hillslope_rast']
subs['slope_rast'] = grassMetadata['slope_rast']
subs['aspect_rast'] = grassMetadata['aspect_rast']
subs['isohyet_rast'] = grassMetadata['zero_rast']
subs['east_horizon_rast'] = grassMetadata['east_horizon_rast']
subs['west_horizon_rast'] = grassMetadata['west_horizon_rast']
subs['patch_rast'] = grassMetadata['patch_rast']
subs['soil_rast'] = grassMetadata['soil_rast']
subs['landuse_rast'] = grassMetadata['landuse_rast']
subs['wetness_index_rast'] = grassMetadata['wetness_index_rast'] 
subs['stratum_rast'] = grassMetadata['stratum_rast']

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
RHESSysMetadata.writeRHESSysEntry(context, 'template', templateFilename)

sys.stdout.write('done\n')

## 4. Run grass2world
worldfileName = templateFilename.replace('template', 'world')
g2wPath = os.path.join(context.projectDir, metadata['g2w_bin'])
worldfilePath = os.path.join(paths.RHESSYS_WORLD, worldfileName)
g2wCommand = "%s -t %s -w %s" % (g2wPath, templateFilepath, worldfilePath)
if args.verbose:
    print(g2wCommand)
sys.stdout.write('\nRunning grass2world...')
sys.stdout.flush()
args = g2wCommand.split()
#print args
process = Popen(args, cwd=paths.RHESSYS_BIN, stdout=PIPE, stderr=PIPE)
(process_stdout, process_stderr) = process.communicate()
#sys.stdout.write(process_stdout)
#sys.stderr.write(process_stderr)
if process.returncode != 0:
    sys.exit("grass2world failed, returning %s" % (process.returncode,) )
RHESSysMetadata.writeRHESSysEntry(context, 'worldfile', worldfileName)

sys.stdout.write('done\n')

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)