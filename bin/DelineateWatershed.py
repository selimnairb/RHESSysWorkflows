#!/usr/bin/env python
"""@package DelineateWatershed

@brief Use GRASS GIS to delineate a watershed for study area defined by a DEM

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

2. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset

3. The following metadata entry(ies) must be present in the study area section of the metadata associated with the project directory:
   dem_rows
   dem_srs
   gage_lat_wgs84
   gage_lon_wgs84
   
4. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
   dem_rast
   
5. The following metadata entry(ies) will be used if present in the GRASS section of the metadata associated with the project directory:
   stream_burned_dem_rast

Post conditions
---------------
1. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   gage_easting_raw (raw gage X coordinate in study area spatial reference system coordinates)
   gage_northing_raw (raw gage Y coordinate in study area spatial reference system coordinates)
   gage_easting_snapped (gage X coordinate, snapped to nearest stream pixel, in study area spatial reference system coordinates)
   gage_northing_snapped (gage Y coordinate, snapped to nearest stream pixel, in study area spatial reference system coordinates)
   watershed_threshold
   watershed_area_km
   watershed_area_estimate_km
    

2. Will write the following entry(ies) to the GRASS section of metadata associated with the project directory:
   gage_vect
   gage_snapped_vect
   drain_rast [drainage direction map]
   uaa_rast [upslope accumulated area]
   basin_rast [delineated watershed boundary]
   subbasins_rast [sub basins within the watershed boundary]
   hillslope_rast [hillslopes within the watershed boundary]
   zone_rast [climate zones, same as hillslope_rast]
   streams_rast [streams within the watershed boundary]
   stream_reaches_rast [streams within the watershed boundary, labeled by reach ID]
   east_horizon_rast
   west_horizon_rast
   slope_rast
   aspect_rast 
   K_rast [default Ksat map]
   m_rast [default decay of Ksat with depth map]
   zero_rast [Map where all cells are set to zero]
   one_rast [Map where all cells are set to one]
   xmap_rast
   ymap_rast
   

Usage:
@code
DelineateWatershedForGRASSLocation.py -p /path/to/project_dir -t 500
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 

@todo fill pits in DEM with GRASS tool, have an argument to turn it off
@todo Factor out gage snapping into a separate script?
"""
import os, sys, errno
import argparse
import ConfigParser
import re
import textwrap

from ecohydrolib.spatialdata.utils import transformCoordinates
from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata

AREA_THRESHOLD = 0.2

def positive_odd_integer(string):
    msg = "%s is not an integer >=3" % (string,)
    value = int(string)
    if value < 2:
        raise argparse.ArgumentTypeError(msg)
    elif value % 2 == 0:
        raise argparse.ArgumentTypeError(msg)
    return value
        

# Handle command line options
parser = argparse.ArgumentParser(description='Delineate watershed using GRASS GIS')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-t', '--threshold', dest='threshold', required=True, type=int,
                    help='Minimum size (in cells the size of the DEM resolution) of watershed sub-basins')
parser.add_argument('-s', '--streamThreshold', dest='streamThreshold', required=False, type=float,
                    help='Threshold to pass to r.findtheriver for distinguishing stream from non-stream pixels')
parser.add_argument('-w', '--streamWindow', dest='streamWindow', required=False, type=positive_odd_integer,
                    help='Stream search window, must be a postive, odd integer')
parser.add_argument('-a', '--areaEstimate', dest='areaEstimate', required=False, type=float,
                    help='Estimated area, in sq. km, of watershed to be delineated.  A warning message will be displayed if the delineated basin area is not close to estimated area.')
parser.add_argument('--ignoreBurnedDEM', dest='ignoreBurnedDEM', action='store_true', required=False,
                    help='Ignore stream burned DEM, if present. Default DEM raster will be used for all operations. If not specified and if stream burned raster is present, stream burned DEM will be used for calculating flow direction maps.')
parser.add_argument('--multiflowdirection', dest='multiflowdirection', action='store_true', required=False,
                    help='Use multiflow direction to determine watershed boundaries.')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing datasets in the GRASS mapset.  If not specified, program will halt if a dataset already exists.')
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

studyArea = RHESSysMetadata.readStudyAreaEntries(context)
if not 'dem_srs' in studyArea:
    sys.exit("Metadata in project directory %s does not contain DEM spatial reference" % (context.projectDir,)) 
if not 'gage_lat_wgs84' in studyArea:
    sys.exit("Metadata in project directory %s does not contain gage latitude" % (context.projectDir,)) 
if not 'gage_lon_wgs84' in studyArea:
    sys.exit("Metadata in project directory %s does not contain gage longitude" % (context.projectDir,)) 
    
grassMetadata = RHESSysMetadata.readGRASSEntries(context)
if not 'dem_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a DEM raster in a GRASS mapset" % (context.projectDir,)) 

demRast = grassMetadata['dem_rast']
demRows = int(studyArea['dem_rows'])

# Determine raster to use for flow direction raster
flowDirDem = demRast
if ('stream_burned_dem_rast' in grassMetadata) and (not args.ignoreBurnedDEM):
    flowDirDem = grassMetadata['stream_burned_dem_rast']
sys.stdout.write("Using raster named '%s' to calculate flow direction map\n" % (flowDirDem,) )

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
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

# Generate drainage direction map
flags = None
if args.multiflowdirection:
    flags = 'f'
result = grassLib.script.run_command('r.watershed', 
                                     elevation=flowDirDem, drainage='drain', accumulation='uaa',
                                     overwrite=args.overwrite,
                                     flags=flags)
if result != 0:
    sys.exit("r.watershed failed creating drainage direction and uaa maps, returning %s" % (result,))

RHESSysMetadata.writeGRASSEntry(context, 'drain_rast', 'drain')
RHESSysMetadata.writeGRASSEntry(context, 'uaa_rast', 'uaa')

# Convert gage coordinates into dem_srs coordinates
(easting, northing) = transformCoordinates(studyArea['gage_lon_wgs84'],
                                           studyArea['gage_lat_wgs84'],
                                           t_srs=studyArea['dem_srs'])

RHESSysMetadata.writeRHESSysEntry(context, 'gage_easting_raw', easting)
RHESSysMetadata.writeRHESSysEntry(context, 'gage_northing_raw', northing)

point = "%f|%f\n" % (easting, northing) 
result = grassLib.script.write_command('v.in.ascii', output='gage', stdin=point, overwrite=args.overwrite)
if result != 0:
    sys.exit("v.in.ascii failed to create 'gage' vector, returning %s" % (result,))

RHESSysMetadata.writeGRASSEntry(context, 'gage_vect', 'gage')

# Snap the gage to the stream
findTheRiver = os.path.join(modulePath, 'r.findtheriver')
if args.streamWindow:
    result = grassLib.script.read_command(findTheRiver, verbose=True,
                                          accumulation="uaa", easting=easting, northing=northing,
                                          threshold=args.streamThreshold,
                                          window=args.streamWindow)
else:
    result = grassLib.script.read_command(findTheRiver, verbose=True,
                                          accumulation="uaa", easting=easting, northing=northing,
                                          threshold=args.streamThreshold)
if None == result or '' == result:
    sys.stdout.write("r.findtheriver did not find a better stream pixel, using raw gage coordinate\n")

snappedCoords = result.split();
if len(snappedCoords) == 2:
    # We found the stream, update coordinates
    easting = float(snappedCoords[0])
    northing = float(snappedCoords[1])
    
RHESSysMetadata.writeRHESSysEntry(context, 'gage_easting_snapped', easting)
RHESSysMetadata.writeRHESSysEntry(context, 'gage_northing_snapped', northing)

point = "%f|%f\n" % (easting, northing) 
result = grassLib.script.write_command('v.in.ascii', output='gage_snapped', stdin=point, overwrite=args.overwrite)
if result != 0:
    sys.exit("v.in.ascii failed to create 'gage_snapped' vector, returning %s" % (result,))

RHESSysMetadata.writeGRASSEntry(context, 'gage_snapped_vect', 'gage_snapped')

# Delineate watershed
basinName = 'basin'
result = grassLib.script.run_command('r.water.outlet', drainage='drain', basin=basinName, 
                                     easting=easting, northing=northing, overwrite=args.overwrite)

if result != 0:
    sys.exit("r.water.outlet failed to delineate watershed basin, returning %s" % (result,))

RHESSysMetadata.writeGRASSEntry(context, 'basin_rast', basinName)

# Generate hillslopes
#   We have to place these options in a dictionary because one of the options
#   has a '.' in its name.
flags = None
if args.multiflowdirection:
    flags = 'f'
rWatershedOptions = {'elevation': flowDirDem, 
                     'threshold': args.threshold,
                     'basin': 'subbasins',
                     'half.basin': 'hillslopes',
                     'stream': 'streams',
                     'overwrite': args.overwrite,
                     'flags': flags }
result = grassLib.script.run_command('r.watershed', **rWatershedOptions)
if result != 0:
    sys.exit("r.watershed failed creating subbasins, returning %s" % (result,))

# Make binary stream layer
# First save stream segment raster
result = grassLib.script.run_command('g.copy', rast='streams,stream_reaches')
if result != 0:
    sys.exit("Failed to save stream reach raster, g.copy returned %s" % (result,))

result = grassLib.script.write_command('r.mapcalc', stdin='streams=(streams >= 0)')
if result != 0:
    sys.exit("r.mapcalc failed to create binary streams, returning %s" % (result,))

RHESSysMetadata.writeGRASSEntry(context, 'subbasins_rast', 'subbasins')
RHESSysMetadata.writeGRASSEntry(context, 'hillslope_rast', 'hillslopes')
RHESSysMetadata.writeGRASSEntry(context, 'stream_reaches_rast', 'stream_reaches')
RHESSysMetadata.writeGRASSEntry(context, 'streams_rast', 'streams')
RHESSysMetadata.writeRHESSysEntry(context, 'watershed_threshold', args.threshold)

# Generate derived terrain products
result = grassLib.script.run_command('r.horizon', flags='d', elevin=demRast, direction=0, horizon='east')
if result != 0:
    sys.exit("r.horizon failed, returning %s" % (result,))
result = grassLib.script.run_command('r.horizon', flags="d", elevin=demRast, direction=180, horizon='west')
if result != 0:
    sys.exit("r.horizon failed, returning %s" % (result,))

result = grassLib.script.write_command('r.mapcalc', stdin='east_horizon=sin(east_0) * 1000')
if result != 0:
    sys.exit("r.mapcalc failed to create east_horizon, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'east_horizon_rast', 'east_horizon')
    
result = grassLib.script.write_command('r.mapcalc', stdin='west_horizon=sin(west_0) * 1000')
if result != 0:
    sys.exit("r.mapcalc failed to create west_horizon, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'west_horizon_rast', 'west_horizon')

result = grassLib.script.run_command('r.slope.aspect', el=demRast, slope='slope', aspect='aspect', overwrite=args.overwrite)
if result != 0:
    sys.exit("r.slope.aspect failed, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'slope_rast', 'slope')
RHESSysMetadata.writeGRASSEntry(context, 'aspect_rast', 'aspect')

result = grassLib.script.run_command('r.topidx', input=demRast, out='wetness_index', overwrite=args.overwrite)
if result != 0:
    sys.exit("r.topidx failed, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'wetness_index_rast', 'wetness_index')

# Generate default K, m, zero, one (default for roads), and patch maps
# First set mask
result = grassLib.script.run_command('r.mask', flags="o", input="basin", maskcats=1)
if result != 0:
    sys.exit("r.mask failed, returning %s" % (result,))

result = grassLib.script.write_command('r.mapcalc', stdin='K=basin*2')
if result != 0:
    sys.exit("r.mapcalc failed to create K map, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'K_rast', 'K')
    
result = grassLib.script.write_command('r.mapcalc', stdin='m=basin*0.12')
if result != 0:
    sys.exit("r.mapcalc failed to create m map, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'm_rast', 'm')
    
result = grassLib.script.write_command('r.mapcalc', stdin='zero=0')
if result != 0:
    sys.exit("r.mapcalc failed to create zero map, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'zero_rast', 'zero')

result = grassLib.script.write_command('r.mapcalc', stdin='one=1')
if result != 0:
    sys.exit("r.mapcalc failed to create one map, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'one_rast', 'one')

result = grassLib.script.write_command('r.mapcalc', stdin='ymap=y()')
if result != 0:
    sys.exit("r.mapcalc failed to create ymap raster, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'ymap_rast', 'ymap')
    
result = grassLib.script.write_command('r.mapcalc', stdin='xmap=x()')
if result != 0:
    sys.exit("r.mapcalc failed to create xmap raster, returning %s" % (result,))
RHESSysMetadata.writeGRASSEntry(context, 'xmap_rast', 'xmap')

# Check delineated basin area
if args.areaEstimate:
    area = -1.0
    areaRegex = re.compile('^\|1\|.*\|(.*)\|$')
    # Get delineated area in hectares
    pipe = grassLib.script.pipe_command('r.report', map=basinName, units='k')
    for line in pipe.stdout:
        m = areaRegex.match(line)
        if m:
            area = float(m.group(1))
            if abs(area - args.areaEstimate) / args.areaEstimate > AREA_THRESHOLD:
                sys.stdout.write(textwrap.fill("WARNING: Delineated area of %.2f sq. km differs from estimated area %.2f sq. km by MORE than %.0f%%. Try increasing or decreasing the stream threshold used for gage snapping.\n" % \
                                   (area, args.areaEstimate, AREA_THRESHOLD * 100) ) )
            else:
                sys.stdout.write(textwrap.fill("OK: Delineated area of %.2f sq. km differs from estimated area %.2f sq. km by less than %.0f%%\n" % \
                                   (area, args.areaEstimate, AREA_THRESHOLD * 100) ) )
    # Write metadata
    RHESSysMetadata.writeRHESSysEntry(context, 'watershed_area_km', area)
    RHESSysMetadata.writeRHESSysEntry(context, 'watershed_area_estimate_km', args.areaEstimate)

sys.stdout.write('\n\nFinished delineating watershed\n')
                
# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)
