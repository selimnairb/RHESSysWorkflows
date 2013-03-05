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

from ecohydroworkflowlib.metadata import GenericMetadata

class RHESSysMetadata(GenericMetadata):
    
    RHESSYS_SECTION = 'rhessys'
    
    @staticmethod
    def writeRHESSysEntry(projectDir, key, value):
        """ Write a RHESSys entry to the metadata store for a given project.
            
            @note Will overwrite a the value for a key that already exists
        
            @param projectDir Path of the project whose metadata store is to be written to
            @param key The key to be written to the RHESSys section of the project metadata
            @param value The value to be written for key stored in the RHESSys section of the project metadata
            
            @exception IOError(errno.EACCES) if the metadata store for the project is not writable
        """
        GenericMetadata._writeEntryToSection(projectDir, RHESSysMetadata.RHESSYS_SECTION, key, value)
     
    @staticmethod
    def readRHESSysEntries(projectDir):
        """ Read all RHESSys entries from the metadata store for a given project
        
            @param projectDir Absolute path of the project whose metadata are to be read
            
            @exception A dictionary of key/value pairs from the RHESSys section of the project metadata
        """
        return GenericMetadata._readEntriesForSection(projectDir, RHESSysMetadata.RHESSYS_SECTION)
    