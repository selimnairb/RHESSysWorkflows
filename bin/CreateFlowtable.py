#!/usr/bin/env python
"""@package CreateFlowtable

@brief Create RHESSys flowtable.

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
   dem_res_x
   dem_res_y

2. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   cf_bin

3. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
   dem_rast
   slope_rast
   streams_rast
   roads_rast [optional]
   roofs_rast [optional]
   impervious_rast [optional]
   
Post conditions
---------------
1. Flowtable will be created in the RHESSys folder of the project directory.

2. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   flowtable

Usage:
@code
CreateFlowtable.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import argparse

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Create RHESSys flowtable using GRASS GIS data and createflowpaths utility')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('--routeRoads', dest='routeRoads', required=False, action='store_true',
                    help='Tell createflowpaths to route flow from roads to the nearest stream pixel (requires roads_rast to be defined in metadata)')
parser.add_argument('--routeRoofs', dest='routeRoofs', required=False, action='store_true',
                    help='Tell createflowpaths to route flow from roof tops based on roof top connectivity to nearest impervious surface (requires roofs_rast and impervious_rast to be defined in metadata)')
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
metadata = RHESSysMetadata.readRHESSysEntries(context)

if not 'dem_res_x' in studyArea:
    sys.exit("Metadata in project directory %s does not contain a DEM x resolution" % (context.projectDir,))
if not 'dem_res_y' in studyArea:
    sys.exit("Metadata in project directory %s does not contain a DEM y resolution" % (context.projectDir,))

if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))
if not 'rhessys_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys directory" % (context.projectDir,))
if not 'cf_bin' in metadata:
    sys.exit("Metadata in project directory %s does not contain a createflowpaths executable" % (context.projectDir,))
    
if not 'dem_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a DEM raster" % (context.projectDir,))
if not 'slope_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a slope raster" % (context.projectDir,))
if not 'streams_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a stream raster" % (context.projectDir,))
    
if args.routeRoads:
    if not 'roads_rast' in grassMetadata:
        sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a roads raster" % (context.projectDir,))

if args.routeRoofs:
    if not 'roofs_rast' in grassMetadata:
        sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a roofs raster" % (context.projectDir,))
    if not 'impervious_rast' in grassMetadata:
        sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a impervious raster" % (context.projectDir,))
    
