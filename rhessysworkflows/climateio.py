"""@package climateio

@brief Routines for reading, modifying, and writing RHESSys climate data.

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
import datetime

from rhessysworkflows.rhessys import readParameterFile


def getStartAndEndDateForClimateStation(climateStation, paths):
    """ Determine start and end date for the climate time-series associated
        with a climate station.  Supports only point time-series.  Does so
        by reading in the daily rain climate file.
    
        @param climateStation String representing path to climate station file
        @param paths rhessysworkflows.rhessys.RHESSysPaths
        
        @return Tuple of datetime.datetime representing start and end date of the climate
        time series; None is returned if the time-series lacks a start date
        
        @raise IOError if unable to read climate station file or daily rain 
        time-series
    """
    if not os.access(climateStation, os.R_OK):
        raise IOError("Unable to read climate station %s" % (climateStation,), errno.EACCES)
    
    station = readParameterFile(climateStation)
    
    rainTimeseriesPath = "%s.rain" % (os.path.join(paths.RHESSYS_DIR, station['daily_climate_prefix']), )
    if not os.access(rainTimeseriesPath, os.R_OK):
        raise IOError("Unable to read daily rain time-series %s" % (rainTimeseriesPath,), errno.EACCES)
    
    # Read daily rain timeseries to determine start and end date
    startDate = None
    endDate = None
    numDays = 0
    startDateRe = re.compile('^(?P<year>\d+)\s(?P<month>\d+)\s(?P<day>\d+)\s(?P<hour>\d+)\s*$')
    countDays = False
    
    f = open(rainTimeseriesPath, 'r')
    for line in f:
        if not countDays:
            line = line.strip()
            result = startDateRe.match(line)
            if result:
                startDate = datetime.datetime(year=int( result.group('year') ),
                                              month=int( result.group('month') ),
                                              day=int( result.group('day') ),
                                              hour=int( result.group('hour') ) )
                countDays = True
                continue
        # Count days
        numDays += 1
    
    if startDate:
        timeDelta = datetime.timedelta(days=numDays)
        endDate = startDate + timeDelta
    
    return (startDate, endDate)
    
    
    