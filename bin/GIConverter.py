#!/usr/bin/env python
"""@package GIConverter

@brief Command line driver program to parameterize green infrastucture defined
in a GI Notebook.

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2016, University of North Carolina at Chapel Hill
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
from rhessysworkflows.command.giconverter import GIConverter
from rhessysworkflows.ginotebook import DEFAULT_HOSTNAME, DEFAULT_API_ROOT

if __name__ == "__main__":

    # Handle command line options
    parser = argparse.ArgumentParser(description='Parameterize green infrastructure for a GI Notebook scenario')
    parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                        help='The configuration file. Must define section "GRASS" and option "GISBASE"')
    parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                        help='The directory to which metadata, intermediate, and final files should be saved')
    parser.add_argument('-s', '--scenario', dest='scenario', required=True, type=int,
                        help='The ID of the GI Scenario whose GI instances are to be parameterized.')
    parser.add_argument('-a', '--authToken', dest='authToken', required=True,
                        help='Authorization token to use for authenticating to the GI Notebook.')
    parser.add_argument('--host', dest='host', required=False, default=DEFAULT_HOSTNAME,
                        help='The hostname of the GI Notebook server.')
    parser.add_argument('--apiRoot', dest='apiRoot', required=False, default=DEFAULT_API_ROOT,
                        help='The root of the API URL to use.')
    parser.add_argument('--useHTTPS', dest='useHTTPS', required=False, action='store_true', default=False,
                        help='Use HTTPS for communication with the GI Notebook.')
    parser.add_argument('-f', '--force', dest='force', action='store_true',
                        help='Force overwrite of existing scenario output.')
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true',
                        help='Print detailed information about what the program is doing')
    args = parser.parse_args()

    configFile = None
    if args.configfile:
        configFile = args.configfile

    command = GIConverter(args.projectDir, configFile)

    exitCode = os.EX_OK
    try:
        command.run(scenario_id=args.scenario,
                    auth_token=args.authToken,
                    host=args.host,
                    api_root=args.apiRoot,
                    use_HTTPS=args.useHTTPS,
                    force=args.force,
                    verbose=args.verbose)
    except CommandException as e:
        print(str(e))
        exitCode = os.EX_DATAERR

    sys.exit(exitCode)
