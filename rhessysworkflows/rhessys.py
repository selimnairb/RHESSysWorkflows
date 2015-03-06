"""@package rhessysworkflows.rhessys
    
@brief Functions related to RHESSys models

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

@todo Add unit tests
"""
import os, errno
import string
from datetime import datetime
from datetime import timedelta
from collections import OrderedDict

import pandas as pd

from rhessysworkflows.metadata import RHESSysMetadata


class RHESSysOutput(object):
    
    TIME_STEP_HOURLY = 1
    TIME_STEP_DAILY = 2
    TIME_STEPS = [TIME_STEP_HOURLY, TIME_STEP_DAILY]
    
    HOUR_HEADER = 'hour'
    DAY_HEADER = 'day'
    MONTH_HEADER = 'month'
    YEAR_HEADER = 'year'
    
    @classmethod
    def readObservedDataFromFile(cls, f, header=True, timeStep=TIME_STEP_DAILY, logger=None,
                                 readHour=True):
        """ Reads the data from the observed data file.  Assumes that
            there is one data point per line.  By default a daily timestep
            is assumed, but hourly is also supported; time step is used for
            calculating date for each datum.
            
            Arguments:
            f -- file object     The text file to read from
            header -- boolean    Specifies whether a header is present
                                  in the file.  If True, the first
                                  line of the file will read and used to
                                  determine start date of the timeseries.
                                  Date is assumed to be in the format:
                                  "YYYY M D H"
            timeStep -- string   One of RHESSysOutput.TIME_STEPS
            readHour -- boolean  Control whether the hour should be read from the file header
        
            Returns tuple (list<datetime.datetime>, list<float>)
            Returns tuple (empty list, list<float>) if header is false  
            Returns tuple of empty lists if there were no data.
        """
        assert(timeStep in RHESSysOutput.TIME_STEPS)
        
        date_list = []
        obs_data = []
        tmpDate = None
        delta = None
        
        if header:
            headerData = f.readline().split()
            if readHour:
                tmpDate = datetime(int(headerData[0]), int(headerData[1]), 
                                   int(headerData[2]), int(headerData[3]) )
            else:
                tmpDate = datetime(int(headerData[0]), int(headerData[1]), 
                                   int(headerData[2]) )
                
            if timeStep == RHESSysOutput.TIME_STEP_HOURLY:
                delta = timedelta(hours=1)
            else:
                delta = timedelta(days=1)
            if logger:
                logger.debug("Observed timeseries begin date: %s" % (str(tmpDate),) )
           
        data = f.readline()
        while data:
            obs_data.append(float(data))
            if header:
                date_list.append(tmpDate)
                tmpDate = tmpDate + delta
            
            data = f.readline()

        return (date_list, obs_data)

    @classmethod
    def readColumnsFromFile(cls, f, column_names, sep=' ', logger=None,
                            readHour=True):
        """ Reads the specified columns from the text file.  The file
            must have a header.  Reads dates/datetime from file by searching
            for headers with names of 'hour', 'day', 'month', 'year'
        
            Arguments:
            f -- file object  The text file to read from
            column_names -- A list of column names to return
            sep -- The field separator (defaults to ' ')
            readHour -- boolean  Control whether the hour should be read from the file header

            Returns Pandas DataFrame object indexed by date
            
            Raises exception if data file does not include year, month, and day fields
        """
        cols = column_names
        if readHour:
            cols = cols + [RHESSysOutput.HOUR_HEADER]
        cols = cols + [RHESSysOutput.DAY_HEADER, 
                 RHESSysOutput.MONTH_HEADER, 
                 RHESSysOutput.YEAR_HEADER]
        df = pd.read_csv(f, sep=' ', usecols=cols)
        # Build index
        time_stamps = None
        try:
            time_stamps = df[RHESSysOutput.YEAR_HEADER].apply(str)
            df = df.drop(RHESSysOutput.YEAR_HEADER, 1)
        except KeyError:
            raise Exception('Data file lacks year column')
        try:
            time_stamps += '/' + df[RHESSysOutput.MONTH_HEADER].apply(str)
            df = df.drop(RHESSysOutput.MONTH_HEADER, 1)
        except KeyError:
            raise Exception('Data file lacks month column')
        try:
            time_stamps += '/' + df[RHESSysOutput.DAY_HEADER].apply(str)
            df = df.drop(RHESSysOutput.DAY_HEADER, 1)
        except KeyError:
            raise Exception('Data file lacks day column')
        try:
            time_stamps += ' ' + df[RHESSysOutput.HOUR_HEADER].apply(str) + '00:00'
            df = df.drop(RHESSysOutput.HOUR_HEADER, 1)
        except KeyError:
            pass
        
        dates = [pd.to_datetime(date) for date in time_stamps]
        datesDf = pd.DataFrame(dates, columns=['datetime'])
        
        df = datesDf.join(df, how='inner')
        df = df.set_index('datetime')
        return df
   

    @classmethod
    def readColumnFromFile(cls, f, column_name, sep=" ", logger=None, startHour=1):
        """ Reads the specified column from the text file.  The file
            must have a header.  Reads dates/datetime from file by searching
            for headers with names of 'hour', 'day', 'month', 'year'
        
            Arguments:
            f -- file object  The text file to read from
            column_name -- The name of the column to return
            sep -- The field separator (defaults to " ")
            startHour -- Hour to use for daily data

            Returns tuple (list<datetime.datetime>, list<float>).  
            Returns tuple of empty lists if the column had no data, or if the column was
            not found
        """
        date_list = []
        col_data = []

        # Read the header line
        header = f.readline()
        headers = string.split(header, sep)
        col_idx = -1
        hour_idx = -1
        day_idx = -1
        month_idx = -1
        year_idx = -1
        col_found = False
        # Find column_name in headers
        for (counter, col) in enumerate(headers):
            if col == column_name:
                col_idx = counter
                col_found = True
            elif col == RHESSysOutput.HOUR_HEADER:
                hour_idx = counter
            elif col == RHESSysOutput.DAY_HEADER:
                day_idx = counter
            elif col == RHESSysOutput.MONTH_HEADER:
                month_idx = counter
            elif col == RHESSysOutput.YEAR_HEADER:
                year_idx = counter
            
        # We found column_name, read the data
        if col_found:
            data = f.readline()
            while data:
                hour = day = month = year = None
                cols = string.split(data, sep)
                # Get data
                col_data.append(float(cols[col_idx]))
                # Get datetime
                if hour_idx >= 0:
                    hour = int(cols[hour_idx])
                if day_idx >= 0:
                    day = int(cols[day_idx])
                if month_idx >= 0:
                    month = int(cols[month_idx])
                if year_idx >= 0:
                    year = int(cols[year_idx])
                # Construct date object
                tmpDate = None
                if hour and day and month and year:
                    tmpDate = datetime(year, month, day, hour)
                elif day and month and year:
                    tmpDate = datetime(year, month, day, startHour)
                elif month and year:
                    tmpDate = datetime(year, month, 1)
                elif year:
                    tmpDate = datetime(year, 12, 31)
                date_list.append(tmpDate)
                
                data = f.readline()

        return (date_list, col_data)

    @classmethod
    def readColumnsFromPatchDailyFile(cls, f, column_names, sep=" "):
        """ Reads the specified columns of data from a RHESSys patch daily output 
            file.  The file must have a header.  Reads dates/datetime from file by searching
            for headers with names of 'hour', 'day', 'month', 'year'
        
            Arguments:
            f -- file object  The text file to read from
            column_names -- List of the names of the columns to return
            sep -- The field separator (defaults to " ")

            Returns collection.OrderedDict<datetime.datetime, dict<string, list<float>>, 
            where the value dict for each datetime key uses column_name as its key.  
            Returns An empty dict if data for the specified columns were not found.
        """
        returnDict = OrderedDict()

        col_idx = {}
        found = False

        # Read the header line
        header = f.readline().strip()
        if ' ' == sep:
            headers = string.split(header)
        else:
            headers = string.split(header, sep)
        hour_idx = -1
        day_idx = -1
        month_idx = -1
        year_idx = -1
        # Find column_name in headers
        for (counter, col) in enumerate(headers):
            if col in column_names:
                col_idx[col] = counter
                found = True
            elif col == RHESSysOutput.HOUR_HEADER:
                hour_idx = counter
            elif col == RHESSysOutput.DAY_HEADER:
                day_idx = counter
            elif col == RHESSysOutput.MONTH_HEADER:
                month_idx = counter
            elif col == RHESSysOutput.YEAR_HEADER:
                year_idx = counter
            
        # We found column_name, read the data
        if found:
            data = f.readline().strip()
            while data and data != '':
                hour = day = month = year = None
                if ' ' == sep:
                    cols = string.split(data)
                else:
                    cols = string.split(data, sep)
                if not len(cols): break;
                # Get datetime
                if hour_idx >= 0:
                    hour = int(cols[hour_idx])
                if day_idx >= 0:
                    day = int(cols[day_idx])
                if month_idx >= 0:
                    month = int(cols[month_idx])
                if year_idx >= 0:
                    year = int(cols[year_idx])
                # Construct date object
                tmpDate = None
                if hour and day and month and year:
                    tmpDate = datetime(year, month, day, hour)
                elif day and month and year:
                    tmpDate = datetime(year, month, day, 1)
                elif month and year:
                    tmpDate = datetime(year, month, 1)
                elif year:
                    tmpDate = datetime(year, 12, 31)
                    
                try:
                    dataForDate = returnDict[tmpDate]
                except KeyError:
                    dataForDate = {}
                    returnDict[tmpDate] = dataForDate
                 
                # Get data
                for key in col_idx:
                    try:
                        tmpData = dataForDate[key]
                    except KeyError:
                        tmpData = []
                        dataForDate[key] = tmpData
                    # TODO: intelligently handle different types    
                    tmpData.append( float(cols[ col_idx[key] ]) )
                
                data = f.readline()

        return (returnDict)

def generateCommandString(binPath, outputPrefix, startDate, endDate, tecPath,
                          worldPath, subsurfaceFlowPath=None, surfaceFlowPath=None,
                          flags="", **kwargs):
    """ Return a string representing a properly formatted RHESSys command with
        the executable and all command line options and arguments specified.
        
        @param binPath String representing path to RHESSys binary
        @param startDate datetime
        @param endDate datetime
        @param tecPath String representing tec file to be used
        @param worldPath String representing world file to be used
        @param subsurfaceFlowPath String representing subsurface flowtable to be used
        @param surfaceFlowPath String representing surface flowtable to be used
        @params flags String representing flags to include (e.g. b for -b or basin output)
        @params **kwargs Mapping type describing calibration options, with key
        representing the parameter name and value a tuple of arguments to pass to the
        calibration option
        
        @return String representing the RHESSys command line 
    """
    cmd = "%s -st %s -ed %s -t %s -w %s" % \
            (binPath,
             datetimeToString(startDate), datetimeToString(endDate),
             tecPath, worldPath)
    if subsurfaceFlowPath:
        cmd = "%s -r %s" % (cmd, subsurfaceFlowPath)
    if surfaceFlowPath and subsurfaceFlowPath:
        cmd = "%s %s" % (cmd, surfaceFlowPath)
    if outputPrefix:
        cmd = "%s -pre %s" % (cmd, outputPrefix)
    # Add flags
    flagsStr = ''
    if len(flags) > 0:
        flagsStr = "-%s" % (flags[0],)
        for c in flags[1:]:
            flagSstr = "%s -%s" % (c,)
        cmd = "%s %s" % (cmd, flagsStr,)
    # Add calibration parameters
    for opt, val in kwargs.iteritems():
        valStr = ' '.join(map(str, val))
        cmd = "%s -%s %s" % (cmd, opt, valStr)
    return cmd
    
    
def datetimeToString(dt):
    """ Return string representing the year, month, day, and hour of a datetime
        object.
        
        @param dt Python datetime object
        
        @return String of the form 'YYYY MM DD HH'
    """
    return "%d %d %d %d" % \
        (dt.year, dt.month, dt.day, dt.hour)


def readParameterFile(paramFilepath):
    """ Read a RHESSys parameter file into a dictionary with
        parameters as keys and parameter values as values
        
        @param paramFilepath String representing path of parameter file to read
        @return Dict with keys representing parameters and their values
        @raise IOError if file cannot be read
    """
    if not os.access(paramFilepath, os.R_OK):
        raise IOError(errno.EACCES, "Unable to read parameter file %s" % (paramFilepath,) )
    
    paramFile = {}
    with open(paramFilepath) as f:
        for line in f:
            tokens = line.strip().split()
            if len(tokens) >= 2 and tokens[0] != '#':
                paramFile[tokens[1].lower()] = tokens[0]
    return paramFile


class RHESSysPaths(object):

    _DB = 'db'
    _ACTIVE = 'active'
    _DIR = 'rhessys'
    _SRC = 'src'
    _TEMPLATES = 'templates'
    _BIN = 'bin'
    _WORLD = 'worldfiles'
    _FLOW = 'flow'
    _TEC = 'tecfiles'
    _DEF = 'defs'
    _CLIM = 'clim'
    _OUT = 'output'
    _OBS = 'obs'
    
    def relpath(self, path):
        """ Return the portion of path relative to self.basedir
        
            @param path String representing a path within self.basedir
            @return The relative path, or None if path was not
            rooted at self.basedir
        """
        relpath = os.path.relpath(path, self.basedir)
        if relpath.find('../') != -1:
            relpath = None
        return relpath
    
    
    def getReclassRulesDirectory(self):
        """ Get path to directory, within the project directory, for storing raster reclass rules in.  
            If the directory does not exist it will be created.
            
            @return String representing the path of the rules directory
        """
        projectDirRuleDir = os.path.join(self.basedir, RHESSysMetadata.RULES_DIR)
        try:
            os.mkdir(projectDirRuleDir)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e
        return projectDirRuleDir
    
    
    def __init__(self, basedir, rhessysDir=_DIR):
            """ Verify that RHESSys directory structure is present,
                creating directories as needed.
    
                @param basedir String representing the path to the directory in which RHESSys directories will be created
                @param rhessysDir String representing root directory into which RHESSys directories will be created
    
                @raise IOError is self.basedir is not writeable.  
                @raise OSError if any directory creation fails.
            """
            self.basedir = os.path.abspath(basedir)
            self.rhessysDir = rhessysDir
            self.RHESSYS_DIR = os.path.join(self.basedir, self.rhessysDir)
            
            # Check for write access in self.basedir
            if not os.access(self.basedir, os.W_OK):
                raise IOError(errno.EACCES, "The directory %s is not writable" 
                              % self.basedir)
            # Create DB directory
            try:
                self.DB_DIR = os.path.join(self.RHESSYS_DIR, self._DB)
                os.makedirs( self.DB_DIR )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create rhessys/src directory
            try:
                self.RHESSYS_SRC = os.path.join(self.RHESSYS_DIR, self._SRC)
                os.makedirs( self.RHESSYS_SRC )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create rhessys/templates directory
            try:
                self.RHESSYS_TEMPLATES = os.path.join(self.RHESSYS_DIR, self._TEMPLATES)
                os.makedirs( self.RHESSYS_TEMPLATES )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create rhessys/bin directory
            try:
                self.RHESSYS_BIN = os.path.join(self.RHESSYS_DIR, self._BIN)
                os.makedirs( self.RHESSYS_BIN )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create rhessys/worldfiles/active directory
            try:
                self.RHESSYS_WORLD = os.path.join(self.RHESSYS_DIR, self._WORLD)
                self.RHESSYS_WORLD_ACTIVE = os.path.join(self.RHESSYS_WORLD, self._ACTIVE)
                os.makedirs( self.RHESSYS_WORLD_ACTIVE )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create rhessys/flow directory
            try:
                self.RHESSYS_FLOW = os.path.join(self.RHESSYS_DIR, self._FLOW)
                os.mkdir( self.RHESSYS_FLOW )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create rhessys/tecfiles/active directory
            try:
                self.RHESSYS_TEC = os.path.join(self.RHESSYS_DIR, self._TEC)
                self.RHESSYS_TEC_ACTIVE  = os.path.join(self.RHESSYS_TEC, self._ACTIVE)
                os.makedirs( self.RHESSYS_TEC_ACTIVE )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create rhessys/defs directory
            try:
                self.RHESSYS_DEF = os.path.join(self.RHESSYS_DIR, self._DEF)
                os.mkdir( self.RHESSYS_DEF )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
            
            # Create rhessys/clim directory
            try:
                self.RHESSYS_CLIM = os.path.join(self.RHESSYS_DIR, self._CLIM)
                os.mkdir( self.RHESSYS_CLIM )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create output directory
            try:
                self.RHESSYS_OUT = os.path.join(self.RHESSYS_DIR, self._OUT)
                os.mkdir( self.RHESSYS_OUT )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e
    
            # Create obs directory
            try:
                self.RHESSYS_OBS = os.path.join(self.RHESSYS_DIR, self._OBS)
                os.mkdir( self.RHESSYS_OBS )
            except OSError as e:
                # If the directory exists, eat the error
                if e.errno != errno.EEXIST:
                    raise e