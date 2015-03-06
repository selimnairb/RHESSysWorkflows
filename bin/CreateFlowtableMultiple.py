#!/usr/bin/env python
"""@package CreateFlowtable

@brief Command line driver program to create multiple RHESSys flowtables,
one flowtable for each worldfile.

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2015, University of North Carolina at Chapel Hill
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
"""
import sys
import os
import argparse

from rhessysworkflows.command.exceptions import *
from rhessysworkflows.command.flowtable import FlowtableMultiple

if __name__ == "__main__":
    
    # Handle command line options
    parser = argparse.ArgumentParser(description='Create RHESSys flowtable using GRASS GIS data and createflowpaths utility')
    parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                        help='The configuration file. Must define section "GRASS" and option "GISBASE"')
    parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                        help='The directory to which metadata, intermediate, and final files should be saved')
    parser.add_argument('--routeRoads', dest='routeRoads', required=False, action='store_true',
                        help='Tell createflowpaths to route flow from roads to the nearest stream pixel (requires roads_rast to be defined in metadata)')
    parser.add_argument('--routeRoofs', dest='routeRoofs', required=False, action='store_true',
                        help='Tell createflowpaths to route flow from roof tops based on roof top connectivity to nearest impervious surface (requires roof_connectivity_rast and impervious_rast to be defined in metadata)')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Run createflowpaths even if DEM x resolution does not match y resolution')
    parser.add_argument('--ignoreBurnedDEM', dest='ignoreBurnedDEM', action='store_true', required=False,
                        help='Ignore stream burned DEM, if present. Default DEM raster will be used for all operations. If not specified and if stream burned raster is present, stream burned DEM will be used for generating the flow table.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Print detailed information about what the program is doing')
    args = parser.parse_args()

    configFile = None
    if args.configfile:
        configFile = args.configfile
        
    command = FlowtableMultiple(args.projectDir, configFile)
    
    exitCode = os.EX_OK
    try: 
        command.run(routeRoads=args.routeRoads, 
                    routeRoofs=args.routeRoofs,
                    ignoreBurnedDEM=args.ignoreBurnedDEM,
                    force=args.force,
                    verbose=args.verbose)
    except CommandException as e:
        print(str(e))
        exitCode = os.EX_DATAERR
    
    sys.exit(exitCode)