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
   dem_columns
   dem_rows

Post conditions
---------------
1. Will write the following entry(ies) to the manifest section of metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset

3. GRASS location and mapset will be created in grass_dbase

4. DEM named 'dem' will be imported into newly created location 

Usage:
@code
PYTHONPATH=${PYTHONPATH}:../EcohydroWorkflowLib python2.7 ./CreateGRASSLocationFromDEM.py -p ../../../scratchspace/scratch7 -g GRASSData -l default -m "Grass location for RHESSys model of Dead Run watershed in Baltimore, MD"
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 

@todo write names of grass datasets to metadata
"""
import os, sys, errno
import argparse
import ConfigParser
import re

import ecohydrologyworkflowlib.metadata as metadata

DEFAULT_MAPSET = 'PERMANENT'

# Handle command line options
parser = argparse.ArgumentParser(description='Import spatial data needed to create RHESSys worldfile into the PERMANENT mapset of a new GRASS location')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-g', '--grassDbase', dest='grassDbase', required=True,
                    help='Path within project directory of the GRASS database where the new location is to be created.')
parser.add_argument('-l', '--location', dest='location', required=True,
                    help='Name of the new GRASS location where study area data are to be imported.')
parser.add_argument('-m', '--description', dest='description', required=True,
                    help='Description for new location')
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

# Make sure grassDbase exists
grassDbase = os.path.join(projectDir, args.grassDbase)
if not os.path.exists(grassDbase):
    (grassDbLoc, grassDbName) = os.path.split(grassDbase)
    if not (os.path.isdir(grassDbLoc) and os.access(grassDbLoc, os.W_OK)):
        sys.exit("%s is not a writable directory" % (grassDbLoc,))
    os.makedirs(grassDbase)
else:
    if not os.access(grassDbase, os.W_OK):
        sys.exit("Not allowed to write to %s" % (grassDbase,))

# Make sure location doesn't already exist, if it does, exit
if os.path.exists(os.path.join(grassDbase, args.location)):
    sys.exit("Location '%s' already exists in %s" % (args.location, grassDbase))

mapset = DEFAULT_MAPSET

# Check for necessary information in metadata
manifest = metadata.readManifestEntries(projectDir)
if not 'dem' in manifest:
    sys.exit("Metadata in project directory %s does not contain a DEM reference" % (projectDir,)) 

studyArea = metadata.readStudyAreaEntries(projectDir)
if not 'dem_srs' in studyArea:
    sys.exit("Metadata in project directory %s does not contain DEM spatial reference" % (projectDir,)) 
srsPattern = re.compile('EPSG:(\d+)')
result = srsPattern.search(studyArea['dem_srs'])
if not result:
    sys.exit("Spatial reference must be specified in the form 'EPSG:<number>'")
srs = int(result.group(1))

# Set up GRASS environment
os.environ['GISBASE'] = gisBase
sys.path.append(os.path.join(gisBase, "etc", "python"))
import grass.script as grass
import grass.script.setup as gsetup
gsetup.init(gisBase, args.grassDbase, args.location)

# Create the new location
grass.core.create_location(grassDbase, args.location, epsg=srs, desc=args.description)

# Import DEM into location
gsetup.init(gisBase,
            grassDbase, args.location, mapset)
demFilepath = os.path.join(projectDir, manifest['dem'])
#print demFilepath
result = grass.run_command('r.in.gdal', flags="e", input=demFilepath, output='dem')
if result != 0:
    sys.exit("Failed to import DEM into new GRASS dataset %s/%s, results:\n%s" % \
             (grassDbase, args.location, result) )

# Set region to DEM
result = grass.run_command('g.region', rast='dem')
if result != 0:
    sys.exit("Failed to set region to DEM")

# Update metadata
metadata.writeManifestEntry(projectDir, "grass_dbase", args.grassDbase)
metadata.writeManifestEntry(projectDir, "grass_location", args.location)
metadata.writeManifestEntry(projectDir, "grass_mapset", mapset)