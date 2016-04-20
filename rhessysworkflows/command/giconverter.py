"""@package rhessysworkflows.command.giconverter

@brief RHESSysWorkflows commands related to parameterizing green infrastructure.

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
import os
import sys
from subprocess import *

from rhessysworkflows.command.base import GrassCommand
from rhessysworkflows.command.exceptions import MetadataException
from rhessysworkflows.command.exceptions import RunException

from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.metadata import RHESSysMetadata


class GIConverter(GrassCommand):

    def __init__(self, projectDir, configFile=None, outfp=sys.stdout):
        """ Construct a GIConverter command.
        Arguments:
        projectDir -- string    The path to the project directory
        configFile -- string    The path to an EcohydroLib configuration file
        outfp -- file-like object    Where output should be written to

        """
        super(GIConverter, self).__init__(projectDir, configFile, outfp)

    def checkMetadata(self, *args, **kwargs):
        """ Check to make sure the project directory has the necessary metadata to run this command.
        """
        super(GIConverter, self).checkMetadata(args, kwargs)

        # Check for necessary information in metadata
        if not 'dem_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a DEM raster" % (self.context.projectDir,))
        if not 'soil_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a soil raster in a GRASS mapset" % (self.context.projectDir,))
        if not 'landcover_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a landcover raster" % (self.context.projectDir,))
        if not 'landuse_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a land use raster" % (self.context.projectDir,))
        if not 'stratum_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a stratum raster" % (self.context.projectDir,))
        if not 'patch_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a patch raster in a GRASS mapset" % (self.context.projectDir,))
        if not 'roads_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a roads raster" % (self.context.projectDir,))
        if not 'slope_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a slope raster" % (self.context.projectDir,))
        if not 'streams_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a stream raster" % (self.context.projectDir,))
        if not 'zero_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a zero raster" % (self.context.projectDir,))

        if not 'dem_res_x' in self.studyArea:
            raise MetadataException("Metadata in project directory %s does not contain a DEM x resolution" % (self.context.projectDir,))
        if not 'dem_res_y' in self.studyArea:
            raise MetadataException("Metadata in project directory %s does not contain a DEM y resolution" % (self.context.projectDir,))

        if not 'grass_dbase' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS Dbase" % (self.context.projectDir,))
        if not 'grass_location' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS location" % (self.context.projectDir,))
        if not 'grass_mapset' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS mapset" % (self.context.projectDir,))
        if not 'rhessys_dir' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a RHESSys directory" % (self.self.context.projectDir,))
        if not 'cf_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a createflowpaths executable" % (self.context.projectDir,))
        if not 'lairead_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a lairead executable" % (self.context.projectDir,))
        if not 'allometric_table' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain an allometric table" % (self.context.projectDir,))
        if not 'template_template' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a template_template" % (self.context.projectDir,))
        if not 'climate_stations' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a list of climate stations" % (self.context.projectDir,))
        if not 'paramdb_dir' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a ParamDB directory" % (self.context.projectDir,))
        if not 'paramdb' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a ParamDB" % (self.context.projectDir,))

    def run(self, *args, **kwargs):
        """ Create flow tables for multiple worldfiles

        Arguments:
        scenario_id -- int    ID of the GI Notebook scenario whose GI instances are to be parameterized.
        host -- string    Hostname of GI Notebook server. Default: None.
        api_path -- string    The root of the API URL to use. Default: None.
        use_HTTPS -- boolean    Use HTTPS for communication with the GI Notebook.
        force -- boolean        Force overwrite of existing scenario output. Default: False.
        verbose -- boolean    Produce verbose output. Default: False.
        """
        scenario_id = kwargs.get('scenario_id')
        if scenario_id is None:
            raise RunException('No scenario ID was specified.')
        host = kwargs.get('host')
        api_path = kwargs.get('api_path')
        use_HTTPS = kwargs.get('use_HTTPS', False)
        force = kwargs.get('force', False)
        verbose = kwargs.get('verbose', False)
