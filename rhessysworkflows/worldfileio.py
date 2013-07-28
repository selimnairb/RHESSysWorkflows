"""@package worldfileio

@brief Routines for reading, modifying, and writing RHESSys worldfiles.

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
    * Neither the name of the University of North Carolina at Chapel Hill nor 
      the names of its contributors may be used to endorse or promote products
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
import os, errno
import re

NUM_BASE_STATION_RE = re.compile('^(\d+)\s+num_base_stations$')
BASE_STATION_RE = re.compile('^(\S+)\s+base_station_filename$')
WORLD_RE = re.compile('^(\d+)\s+world_ID$')

class WorldfileParseError(Exception):
    pass

def getClimateBaseStationFilenames(worldfileHeader, strict=True):
    """ Read climate base station paths from the header of a worldfile
        
        @param worldfileHeader String representing path of worldfile header 
        from which to read climate base stations
        @param strict True if strict parsing should be used
        
        @return list representing climate base stations paths found in the 
        worldfile header
        
        @raise IOError if unable to read worldfile header
        @raise WorldfileParseError if there appears to be an error in the
        worldfile header structure
    """
    if not os.access(worldfileHeader, os.R_OK):
        raise IOError("Unable to read worldfile %s" % (worldfileHeader,), errno.EACCES)
    
    numBaseStations = None
    baseStations = []
    
    f = open(worldfileHeader, 'r')
    for line in f:
        line = line.strip()        
    
        result = NUM_BASE_STATION_RE.match(line)
        if result:
            numBaseStations = int(result.group(1))
            continue
        result = BASE_STATION_RE.match(line)
        if result:
            baseStations.append( result.group(1) )
            continue
    
    if strict:
        if numBaseStations != len(baseStations):
            raise WorldfileParseError("Expected %d base stations, but found %d" %
                                      (numBaseStations, len(baseStations)) )
            
    return baseStations
        