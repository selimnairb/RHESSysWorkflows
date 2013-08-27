#!/usr/bin/env python
"""@package ImportClimateData

@brief Import climate station and corrsponding data, already in RHESSys format, 
into project directory

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
   rhessys_dir
   
Post conditions
---------------
1. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   climate_stations


Usage:
@code
ImportClimateData.py -p /path/to/project_dir -s /path/to/existing/rhessys/climate/data
@endcode
"""
import os, sys, errno
import argparse
import re
import shutil
import textwrap

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

STATION_FILE_EXTENSION = 'base'

# Handle command line options
parser = argparse.ArgumentParser(description='Import RHESSys climate data into project directory')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-s', '--sourceDir', dest='sourceDir', required=True,
                    help='The directory from which climate data should be copied. Assumes climate base stations are stored in files ending in ".base", with climate data files of the form ".VARNAME" (e.g. ".tmin")')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing climate stations and datasets; If specified, will delete existing data before importing new data.  If not specified, new data will be added to existing data.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile)

# Check for necessary information in metadata
metadata = RHESSysMetadata.readRHESSysEntries(context)
paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])

if not os.access(args.sourceDir, os.R_OK):
    sys.exit("The specified path of the climate data source directory, %s, is not readable" % (args.sourceDir,) )
if not os.path.isdir(args.sourceDir):
    sys.exit("The specified path of the climate data source directory, %s, is not a directory" % (args.sourceDir,) )
    
if args.overwrite:
    # Delete any existing climate data
    contents = os.listdir(paths.RHESSYS_CLIM)
    for entry in contents:
        fileToDelete = os.path.join(paths.RHESSYS_CLIM, entry)
        print("Deleting existing climate file %s" % (fileToDelete,) )
        os.unlink(fileToDelete)
    
# Get listing of climate stations in source directory
stationRegex = re.compile("^(.+)\.%s$" % (STATION_FILE_EXTENSION,) )
contents = os.listdir(args.sourceDir)
stations = []
for entry in contents:
    m = stationRegex.match(entry)
    if m:
        stations.append(m.group(1))    

# Copy station file and climate data
sys.stdout.write(textwrap.fill("Importing climate data from %s...\n" % (args.sourceDir,) ) )
sys.stdout.flush()
for station in stations:
    # Copy station file
    sys.stdout.write("\n\tStation '%s'\n" % (station,) )
    sys.stdout.flush()
    stationFileName = "%s%s%s" % (station, os.extsep, STATION_FILE_EXTENSION)
    stationFilePath = os.path.join(args.sourceDir, stationFileName)
    shutil.copy(stationFilePath, paths.RHESSYS_CLIM)
    dataRegex = re.compile("^%s\.(.+)$" % (station,) )
    # Look for climate data files to copy and copy them
    for entry in contents:
        m = dataRegex.match(entry)
        if m:
            extension = m.group(1)
            if extension != STATION_FILE_EXTENSION:
                shutil.copy( os.path.join(args.sourceDir, entry), paths.RHESSYS_CLIM )
sys.stdout.write('done\n')

# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'climate_stations', RHESSysMetadata.VALUE_DELIM.join(stations))

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)
  