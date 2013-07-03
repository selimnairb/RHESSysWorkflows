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

from rhessysworkflows.metadata import RHESSysMetadata

def generateCommandString(binPath, outputPrefix, startDate, endDate, tecPath,
                          worldPath, surfaceFlowPath, subsurfaceFlowPath=None,
                          flags="", **kwargs):
    """ Return a string representing a properly formatted RHESSys command with
        the executable and all command line options and arguments specified.
        
        @param binPath String representing path to RHESSys binary
        @param startDate datetime
        @param endDate datetime
        @param tecPath String representing tec file to be used
        @param worldPath String representing world file to be used
        @param surfaceFlowPath String representing surface flowtable to be used
        @param subsurfaceFlowPath String representing subsurface flowtable to be used
        @params flags String representing flags to include (e.g. b for -b or basin output)
        @params **kwargs Mapping type describing calibration options, with key
        representing the parameter name and value a tuple of arguments to pass to the
        calibration option
        
        @return String representing the RHESSys command line 
    """
    cmd = "%s -st %s -ed %s -t %s -w %s -r %s" % \
            (binPath,
             datetimeToString(startDate), datetimeToString(endDate),
             tecPath, worldPath, surfaceFlowPath)
    if outputPrefix:
        cmd = "%s -pre %s" % (cmd, outputPrefix)
    if subsurfaceFlowPath:
        cmd = "%s %s" % (cmd, subsurfaceFlowPath)
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