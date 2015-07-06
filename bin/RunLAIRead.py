#!/usr/bin/env python
"""@package RunLAIRead

@brief Run lairead utility to initializes vegetation carbon stores. Will: (1) run lairead to
produce a redefine worldfile; (2) run RHESSys simulation for 3-days to generate base worldfile

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
1. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset
   rhessys_dir
   rhessys_bin
   lairead_bin
   worldfile_zero
   surface_flowtable
   subsurface_flowtable
   allometric_table

2. The following metadata entry(ies) must be present in the GRASS section of the metadata associated with the project directory:
   basin_rast
   dem_rast
   hillslope_rast
   zone_rast
   patch_rast
   stratum_rast
   lai_rast
   
Post conditions
---------------
1. Worldfile with initialized vegetation carbon stores will be saved to the appropriate location of the project directory

2. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   worldfile
   tec_lairead

Usage:
@code
RunLAIRead.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified. 
"""
import argparse
import datetime
from subprocess import *
import shutil

from ecohydrolib.grasslib import *

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.rhessys import datetimeToString
from rhessysworkflows.rhessys import generateCommandString
from rhessysworkflows.worldfileio import getClimateBaseStationFilenames
from rhessysworkflows.climateio import getStartAndEndDateForClimateStation

# Handle command line options
parser = argparse.ArgumentParser(description='Run lairead utility to initializes vegetation carbon stores. Will: (1) run lairead to ' +
                                             'produce a redefine worldfile; (2) run RHESSys simulation for 3-days to generate base worldfile')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                    help='Print detailed information about what the program is doing')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
grassMetadata = RHESSysMetadata.readGRASSEntries(context)
if not 'basin_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a basin raster" % (context.projectDir,))
if not 'dem_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a DEM raster" % (context.projectDir,))
if not 'hillslope_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a hillslope raster" % (context.projectDir,))  
if not 'zone_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a zone raster" % (context.projectDir,)) 
if not 'patch_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a patch raster" % (context.projectDir,)) 
if not 'stratum_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with a stratum raster" % (context.projectDir,)) 
if not 'lai_rast' in grassMetadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS dataset with an LAI raster" % (context.projectDir,)) 

metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))
if not 'rhessys_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys directory" % (context.projectDir,))
if not 'rhessys_bin' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys binary" % (context.projectDir,))
if not 'lairead_bin' in metadata:
    sys.exit("Metadata in project directory %s does not contain a lairead executable" % (context.projectDir,))
if not 'worldfile_zero' in metadata:
    sys.exit("Metadata in project directory %s does not contain an initial worldfile" % (context.projectDir,))
if not 'surface_flowtable' in metadata:
    sys.exit("Metadata in project directory %s does not contain a surface flowtable" % (context.projectDir,))
if not 'subsurface_flowtable' in metadata:
    sys.exit("Metadata in project directory %s does not contain a subsurface flowtable" % (context.projectDir,))
if not 'allometric_table' in metadata:
    sys.exit("Metadata in project directory %s does not contain an allometric table" % (context.projectDir,))

rhessysDir = metadata['rhessys_dir']
paths = RHESSysPaths(args.projectDir, rhessysDir)

worldfileZero = metadata['worldfile_zero']
headerZero = "%s.hdr" % (worldfileZero,)
worldfileZeroPath = os.path.join(context.projectDir, worldfileZero)
worldfileDir = os.path.dirname(worldfileZeroPath)

# Set up GRASS environment
modulePath = context.config.get('GRASS', 'MODULE_PATH')
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

## Make sure mask and region are properly set
demRast = grassMetadata['dem_rast']
result = grassLib.script.run_command('g.region', rast=demRast)
if result != 0:
    sys.exit("g.region failed to set region to DEM, returning %s" % (result,))

basinRast = grassMetadata['basin_rast']
result = grassLib.script.run_command('r.mask', flags='o', input=basinRast, maskcats='1')
if result != 0:
    sys.exit("r.mask failed to set mask to basin, returning %s" % (result,))

## 1. Determine legal simulation start and date from climate data 
# Read first climate station from worldfile
headerZeroPath = os.path.join(context.projectDir, headerZero)
stations = getClimateBaseStationFilenames(headerZeroPath)
assert( len(stations) )
firstStationPath = os.path.normpath( os.path.join(paths.RHESSYS_DIR, stations[0]) )
if args.verbose:
    sys.stdout.write("First climate station in worldfile: %s\n" % (firstStationPath,) )

# Read climate timeseries for start and end date, write to metadata
(startDate, endDate) = getStartAndEndDateForClimateStation(firstStationPath, paths)
if args.verbose:
    sys.stdout.write("\tstart date: %s, end date: %s\n" % ( str(startDate), str(endDate) ) )
fourDays = datetime.timedelta(days=4)
if endDate - startDate < fourDays:
    sys.exit("Climate time-series defined by station %s is too short to run lairead (less than four-days long)" %
             (firstStationPath,) )

## 2. Run LAI read to generate redefine worldfile
tecDurRedef = datetime.timedelta(days=1)
tecRedef = startDate + tecDurRedef
laireadPath = os.path.join(context.projectDir, metadata['lairead_bin'])
oldWorldPath = os.path.join(context.projectDir, worldfileZero)
redefWorldName = "%s.Y%dM%dD%dH%d" % \
    (worldfileZero, tecRedef.year, tecRedef.month, tecRedef.day, tecRedef.hour)
redefWorldPath = os.path.join(context.projectDir, redefWorldName)
allomPath = os.path.join(context.projectDir, metadata['allometric_table'])

if args.verbose:
    sys.stdout.write("Running lairead to generate redefine worldfile...\n")
p = grassLib.script.pipe_command(laireadPath, old=oldWorldPath, redef=redefWorldPath,
                                      allom=allomPath, lai=grassMetadata['lai_rast'],
                                      vegid=grassMetadata['stratum_rast'],
                                      zone=grassMetadata['zone_rast'],
                                      hill=grassMetadata['hillslope_rast'],
                                      patch=grassMetadata['patch_rast'],
                                      mask=grassMetadata['basin_rast'])
(stdoutStr, stderrStr) = p.communicate() 
result = p.returncode
if result != 0:
    sys.stdout.write(stdoutStr)
    sys.exit("\nlairead failed, returning %s" % (result,))
if args.verbose:
    if stdoutStr:
        sys.stdout.write(stdoutStr)
    if stderrStr:
        sys.stdout.write(stderrStr)

## 3. Write TEC file for redefining the initial world file
##    Redefine on the second day of the simulation, write output
##    on the third day
tecName = 'tec.lairead'
tecPath = os.path.join(paths.RHESSYS_TEC, tecName)
tecDurOutput = datetime.timedelta(days=2)
tecOutput = startDate + tecDurOutput

f = open(tecPath, 'w')
f.write("%s redefine_world%s" % 
        (datetimeToString(tecRedef), os.linesep) )
f.write("%s output_current_state%s" %
        (datetimeToString(tecOutput), os.linesep) )
f.close()
RHESSysMetadata.writeRHESSysEntry( context, 'tec_lairead', paths.relpath(tecPath) )

## 4. Run RHESSys for the first 4 legal days with redefine TEC
rhessysStart = startDate
rhessysDur = datetime.timedelta(days=3)
rhessysEnd = startDate + rhessysDur
surfaceFlowtablePath = os.path.join(context.projectDir, metadata['surface_flowtable'])
subSurfaceFlowtablePath = os.path.join(context.projectDir, metadata['subsurface_flowtable'])
rhessysBinPath = os.path.join(context.projectDir, metadata['rhessys_bin'])

rhessysCmd = generateCommandString(rhessysBinPath, None,
                                   rhessysStart, rhessysEnd,
                                   tecPath, oldWorldPath,
                                   subSurfaceFlowtablePath, surfaceFlowtablePath)
if args.verbose:
    print(rhessysCmd)
sys.stdout.write('\nRunning RHESSys to redefine worldfile with vegetation carbon stores...')
sys.stdout.flush()

cmdArgs = rhessysCmd.split()
process = Popen(cmdArgs, cwd=paths.RHESSYS_DIR, stdout=PIPE, stderr=PIPE)
(process_stdout, process_stderr) = process.communicate()
if args.verbose:
    sys.stdout.write(process_stdout)
    sys.stderr.write(process_stderr)
if process.returncode != 0:
    sys.exit("\n\nRHESSys failed, returning %s" % (process.returncode,) )

sys.stdout.write('done\n')

## 5. Rename redefine worldfile, write to metadata
outputWorldName = "%s.Y%dM%dD%dH%d.state" % \
    (worldfileZero, tecOutput.year, tecOutput.month, tecOutput.day, tecOutput.hour)
outputWorldPath = os.path.join(context.projectDir, outputWorldName)

if not os.access(outputWorldPath, os.W_OK):
    sys.exit("Unable to find redefined worldfile %s" % (outputWorldPath,) )
    
newWorldName = 'world'
newWorldPath = os.path.join(paths.RHESSYS_WORLD, newWorldName)

shutil.move(outputWorldPath, newWorldPath)
if not os.path.exists(newWorldPath):
    sys.exit("Failed to copy redefined worldfile %s to %s" % (outputWorldPath, newWorldPath) )
RHESSysMetadata.writeRHESSysEntry( context, 'worldfile', paths.relpath(newWorldPath) )

# Copy world file header from init worldfile to final world file
header = "%s.hdr" % (newWorldName,)
headerPath = os.path.join(paths.RHESSYS_WORLD, header)
shutil.copyfile(headerZeroPath, headerPath)

sys.stdout.write('\n\nSuccessfully used lairead to initialize vegetation carbon stores.\n')

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)