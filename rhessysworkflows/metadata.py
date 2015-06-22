"""@package rhessysworkflows.metadata
    
@brief Classes for writing and reading metadata for RHESSys workflows

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
"""
import os
import errno
import ConfigParser

from ecohydrolib.metadata import GenericMetadata
import ecohydrolib.metadata as metadata
from ecohydrolib.metadata import MetadataVersionError

import ecohydrolib.command.landcover

import rhessysworkflows

class WorkflowVersionError(MetadataVersionError):
    def __init__(self, workflowVersion):
        self.workflowVersion = workflowVersion
        self._workflowVersion = rhessysworkflows.__version__
    def __str__(self):
        return repr("Version %s of RHESSysWorkflows was used to write the metadata, but you are running version %s." %\
                    (self.workflowVersion, self._workflowVersion) )


class RHESSysMetadata(GenericMetadata):
    """ Handles metadata persistance for RHESSys workflows.  Extends ecohydrolib.GenericMetadata class.
    
        @note All keys are stored in lower case.
        @note This object is stateless, all methods are static, writes to metadata store
        are written immediately.
    """
    
    _workflowVersion = rhessysworkflows.__version__
    
    VERSION_KEY = 'rhessysworkflows_version'
    
    MODEL_NAME = 'rhessys'
    RHESSYS_SECTION = MODEL_NAME
    # Patch list of valid sections
    GenericMetadata.SECTIONS.append(RHESSYS_SECTION)
   
    RULES_DIR = 'rules' 
    KNOWN_LC_TYPES = ecohydrolib.command.landcover.KNOWN_LC_TYPES
    LC_RULE_ROAD = 'road.rule'
    LC_RULE_IMPERVIOUS = 'impervious.rule'
    LC_RULE_LANDUSE = 'landuse.rule'
    LC_RULE_STRATUM = 'stratum.rule'
    LC_RULE_LAI_COMPAT = 'lai.rule'
    LC_RULE_LAI = 'lai-recode.rule'
    LC_RULES = [LC_RULE_ROAD, LC_RULE_IMPERVIOUS, LC_RULE_LANDUSE, LC_RULE_STRATUM, LC_RULE_LAI]
    SOILS_RULE = 'soils.rule'
    SOILS_RULES = [SOILS_RULE]
    
    @staticmethod
    def checkWorkflowVersion(projectDir):
        """ Check if metadata store is compatible with current version of RHESSysWorkflows. Accepts
            project directory as this method is used in the constructor to the Context class.
        
            @param projectDir, the path of the project whose metadata store is to be written to
            @raise WorkflowVersionError if a version already exists in the metadata store
            and is different than RHESSysMetadata._workflowVersion
        """
        metadataFilepath = os.path.join(projectDir, GenericMetadata.METADATA_FILENAME)
        if os.path.exists(metadataFilepath):
            if not os.access(metadataFilepath, os.R_OK):
                raise IOError(errno.EACCES, "Unable to read metadata store for project %s" % \
                              (projectDir,))
            # Read metadata store
            config = ConfigParser.RawConfigParser()
            config.read(metadataFilepath)
            if config.has_section(RHESSysMetadata.RHESSYS_SECTION):
                if config.has_option(RHESSysMetadata.RHESSYS_SECTION, \
                                 RHESSysMetadata.VERSION_KEY):
                    workflowVersion = config.get(RHESSysMetadata.RHESSYS_SECTION, \
                                     RHESSysMetadata.VERSION_KEY)
                    if workflowVersion != RHESSysMetadata._workflowVersion:
                        raise WorkflowVersionError(workflowVersion)


    @staticmethod
    def _writeWorkflowVersionToMetadata(config):
        """ Write RHESSysWorkflows version to RHESSYS_SECTION of metadata.
        
            @param config ConfigParser to write version information to
            @raise WorkflowVersionError if a version already exists in the metadata store
            and is different than RHESSysMetadata._workflowVersion
        """
        if not config.has_section(RHESSysMetadata.RHESSYS_SECTION):
            config.add_section(RHESSysMetadata.RHESSYS_SECTION)
        
        if not config.has_option(RHESSysMetadata.RHESSYS_SECTION, \
                             RHESSysMetadata.VERSION_KEY):
            config.set(RHESSysMetadata.RHESSYS_SECTION, \
                       RHESSysMetadata.VERSION_KEY, RHESSysMetadata._workflowVersion)
            return
            
        workflowVersion = config.get(RHESSysMetadata.RHESSYS_SECTION, \
                                     RHESSysMetadata.VERSION_KEY)
        if workflowVersion != RHESSysMetadata._workflowVersion:
            raise WorkflowVersionError(workflowVersion)
    
    @staticmethod
    def writeRHESSysEntry(context, key, value):
        """ Write a RHESSys entry to the metadata store for a given project.
            
            @note Will overwrite the value for a key that already exists
        
            @param context Context object containing projectDir, the path of the project whose 
            metadata store is to be written to
            @param key The key to be written to the RHESSys section of the project metadata
            @param value The value to be written for key stored in the RHESSys section of the project metadata
            
            @exception IOError(errno.EACCES) if the metadata store for the project is not writable
        """
        GenericMetadata.writeEntryToSection(context, RHESSysMetadata.RHESSYS_SECTION, key, value, \
                                            RHESSysMetadata._writeWorkflowVersionToMetadata)
    
    
    @staticmethod
    def deleteRHESSysEntry(context, key):
        """ Delete a RHESSys entry from the metadata store for a given project.
        
            @param context Context object containing projectDir, the path of the project whose 
            metadata store is to be deleted from
            @param key The key to be deleted from the RHESSys section of the project metadata
            
            @exception IOError(errno.EACCES) if the metadata store for the project is not writable
        """
        GenericMetadata.deleteEntryFromSection(context, RHESSysMetadata.RHESSYS_SECTION, key, \
                                               RHESSysMetadata._writeWorkflowVersionToMetadata)
         
     
    @staticmethod
    def readRHESSysEntries(context):
        """ Read all RHESSys entries from the metadata store for a given project
        
            @param context Context object containing projectDir, the path of the project whose 
            metadata store is to be read from
            
            @exception A dictionary of key/value pairs from the RHESSys section of the project metadata
        """
        return GenericMetadata._readEntriesForSection(context.projectDir, RHESSysMetadata.RHESSYS_SECTION)
    

class ModelRun(metadata.ModelRun):
    # Register model name with EcohydroLib metadata
    GenericMetadata.MODEL_TYPES.append(RHESSysMetadata.MODEL_NAME)
    
    def __init__(self):
        super(ModelRun, self).__init__(RHESSysMetadata.MODEL_NAME)