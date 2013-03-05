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
   soil_raster_avgsand
   soil_raster_avgclay

2. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   
3. Requires r.soils.texture GRASS extension: http://grasswiki.osgeo.org/wiki/GRASS_AddOns#r.soils.texture

Post conditions
---------------
1. The following raster datasets will be created in the GRASS location:
   soil_raster_avgclay,
   soil_raster_avgsand,
   soil_texture

Usage:
@code
PYTHONPATH=${PYTHONPATH}:../EcohydroWorkflowLib python2.7 ./GenerateSoilTextureMap.py -p ../../../scratchspace/scratch7
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import os, sys, errno
import argparse
import ConfigParser

from rhessysworkflows.metadata import RHESSysMetadata

# Handle command line options
parser = argparse.ArgumentParser(description='Generate soil texture map for dataset in GRASS GIS')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
args = parser.parse_args()

configFile = None
if args.configfile:
    configFile = args.configfile
else:
    try:
        configFile = os.environ['ECOHYDROWORKFLOW_CFG']
    except KeyError:
        sys.exit("Configuration file not specified via environmental variable\n'ECOHYDROWORKFLOW_CFG', and -i option not specified")
if not os.access(configFile, os.R_OK):
    raise IOError(errno.EACCES, "Unable to read configuration file %s" %
                  configFile)
config = ConfigParser.RawConfigParser()
config.read(configFile)

gisBase = config.get('GRASS', 'GISBASE')
modulePath = config.get('GRASS', 'MODULE_PATH')
moduleEtc = config.get('GRASS', 'MODULE_ETC')

schemePath = os.path.join(moduleEtc, 'USDA.dat')
if not os.access(schemePath, os.R_OK):
    raise IOError(errno.EACCES, "Not allowed to read r.soils.texture scheme %s" % (schemePath,) )

if args.projectDir:
    projectDir = args.projectDir
else:
    projectDir = os.getcwd()
if not os.path.isdir(projectDir):
    raise IOError(errno.ENOTDIR, "Project directory %s is not a directory" % (projectDir,))
if not os.access(projectDir, os.W_OK):
    raise IOError(errno.EACCES, "Not allowed to write to project directory %s" %
                  projectDir)
projectDir = os.path.abspath(projectDir)

# Check for necessary information in metadata
manifest = RHESSysMetadata.readManifestEntries(projectDir)
if not 'soil_raster_avgsand' in manifest:
    sys.exit("Metadata in project directory %s does not contain a soil_raster_avgsand raster" % (projectDir,))
if not 'soil_raster_avgclay' in manifest:
    sys.exit("Metadata in project directory %s does not contain a soil_raster_avgclay raster" % (projectDir,))

metadata = RHESSysMetadata.readRHESSysEntries(projectDir)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (projectDir,))

# Set up GRASS environment
grassDbase = os.path.join(projectDir, metadata['grass_dbase'])
os.environ['GISBASE'] = gisBase
sys.path.append(os.path.join(gisBase, "etc", "python"))
import grass.script as grass
import grass.script.setup as gsetup
gsetup.init(gisBase, grassDbase, metadata['grass_location'], metadata['grass_mapset'])

# Import percent sand and percent clay raster maps into GRASS
percentSandRasterPath = os.path.join(projectDir, manifest['soil_raster_avgsand'])
result = grass.run_command('r.in.gdal', input=percentSandRasterPath, output='soil_raster_avgsand')
if result != 0:
    sys.exit("Failed to import soil_raster_avgsand into GRASS dataset %s/%s, results:\n%s" % \
             (grassDbase, metadata['grass_location'], result) )
    
percentClayRasterPath = os.path.join(projectDir, manifest['soil_raster_avgclay'])
result = grass.run_command('r.in.gdal', input=percentClayRasterPath, output='soil_raster_avgclay')
if result != 0:
    sys.exit("Failed to import soil_raster_avgclay into GRASS dataset %s/%s, results:\n%s" % \
             (grassDbase, metadata['grass_location'], result) )

# Generate soil texture map
soilTexture = os.path.join(modulePath, 'r.soils.texture')
result = grass.read_command(soilTexture, sand='soil_raster_avgsand', clay='soil_raster_avgclay',
                            scheme=schemePath, output='soil_texture')
if None == result:
    sys.exit("r.soils.texture failed, returning %s" % (result,))