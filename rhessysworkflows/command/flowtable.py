"""@package rhessysworkflows.command.flowtable
    
@brief RHESSysWorkflows commands related to flowtables

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
import os
import sys
from subprocess import *

from rhessysworkflows.command.base import GrassCommand
from rhessysworkflows.command.exceptions import MetadataException
from rhessysworkflows.command.exceptions import RunException

from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.metadata import RHESSysMetadata

class FlowtableMultiple(GrassCommand):
    
    def __init__(self, projectDir, configFile=None, outfp=sys.stdout):
        """ Construct a FlowtableMultiple command.
        Arguments:
        projectDir -- string    The path to the project directory
        configFile -- string    The path to an EcohydroLib configuration file
        outfp -- file-like object    Where output should be written to
        
        """
        super(FlowtableMultiple, self).__init__(projectDir, configFile, outfp)
    
    def checkMetadata(self, *args, **kwargs):
        """ Check to make sure the project directory has the necessary metadata to run this command.
        """
        super(FlowtableMultiple, self).checkMetadata(args, kwargs)
        
        # Check for necessary information in metadata
        if not 'dem_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a DEM raster" % (self.context.projectDir,))
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
        
        if not 'rhessys_dir' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a RHESSys directory" % (self.self.context.projectDir,))
        if not 'cf_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a createflowpaths executable" % (self.context.projectDir,))
        if not 'subbasin_masks' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain multiple worldfile masks" % (self.context.projectDir,))
        if not 'template' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a template" % (self.context.projectDir,))
        
        routeRoads = kwargs.get('routeRoads', False)
        if routeRoads:
            if not 'roads_rast' in self.grassMetadata:
                raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a roads raster" % (self.context.projectDir,))
        
        routeRoofs = kwargs.get('routeRoofs', False)
        if routeRoofs:
            if not 'roof_connectivity_rast' in self.grassMetadata:
                raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a roofs raster" % (self.context.projectDir,))
        if not 'impervious_rast' in self.grassMetadata:
                raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a impervious raster" % (self.context.projectDir,))
        
    def run(self, *args, **kwargs):
        """ Create flow tables for multiple worldfiles 
        
        Arguments:
        routeRoads -- boolean    Whether road routing should be enabled in createflowpaths. Default: False.
        routeRoofs -- boolean    Whether roof routing should be enabled in createflowpaths. Default: False.
        ignoreBurnedDEM -- boolean    If true, use the base DEM when running createflowpaths. 
                                      If false, use the stream-burned DEM (if present).  Default: False.
        force -- boolean        Whether to force createflowpaths to run if DEM X resolution != Y resolution. Default: False.
        verbose -- boolean    Produce verbose output. Default: False.
        """
        routeRoads = kwargs.get('routeRoads', False)
        routeRoofs = kwargs.get('routeRoofs', False)
        force = kwargs.get('force', False)
        ignoreBurnedDEM = kwargs.get('ignoreBurnedDEM', False)
        verbose = kwargs.get('verbose', False)
        
        self.checkMetadata(routeRoads=routeRoads, 
                           routeRoofs=routeRoofs)
        
        rhessysDir = self.metadata['rhessys_dir']
        self.paths = RHESSysPaths(self.context.projectDir, rhessysDir)
        
        demResX = float(self.studyArea['dem_res_x'])
        demResY = float(self.studyArea['dem_res_y'])
        if demResX != demResY:
            self.outfp.write("DEM x resolution (%f) does not match y resolution (%f)" %
                             (demResX, demResY) )
            if not force:
                raise RunException('Exiting.  Use force option to override')
        
        # Determine DEM raster to use
        demRast = self.grassMetadata['dem_rast']
        if ('stream_burned_dem_rast' in self.grassMetadata) and (not ignoreBurnedDEM):
            demRast = self.grassMetadata['stream_burned_dem_rast']
        self.outfp.write("Using raster named '%s' to calculate flow direction map\n" % (demRast,) )
        
        # Make sure region is properly set
        demRast = self.grassMetadata['dem_rast']
        result = self.grassLib.script.run_command('g.region', rast=demRast)
        if result != 0:
            raise RunException("g.region failed to set region to DEM, returning {0}".format(result))
        
        # Get paths for CF binary and template
        cfPath = os.path.join(self.context.projectDir, self.metadata['cf_bin'])
        templatePath = os.path.join(self.context.projectDir, self.metadata['template'])
        if verbose:
            self.outfp.write(self.templatePath)
            self.outfp.write('\n')
        
        # Make output file paths and file name templates
        flowTableNameBase = "world_{mask}"
        flowOutpath = os.path.join(self.paths.RHESSYS_FLOW, flowTableNameBase)
        cfOutpath = os.path.join(self.paths.RHESSYS_FLOW, "cf_{mask}.out")
        
        roads = None
        if routeRoads:
            roads = self.grassMetadata['roads_rast']
        else:
            roads = self.grassMetadata['zero_rast']
        
        roofs = None
        impervious = None
        
        # These filenames are only for metadata
        if routeRoofs:
            roofs = self.grassMetadata['roof_connectivity_rast']
            impervious = self.grassMetadata['impervious_rast']
            surfaceFlowtableTemplate = "world_{mask}_surface.flow"
            subsurfaceFlowtableTemplate = "world_{mask}_subsurface.flow"
        else:
            surfaceFlowtableTemplate = subsurfaceFlowtableTemplate = "world_{mask}.flow"
        
        # Make flowtable for each masked region
        if verbose:
            self.outfp.write('Running createflowpaths (this may take a few minutes)...')
            self.outfp.flush()
        
        surfaceFlowtables = []
        subsurfaceFlowtables = []
        masks = self.metadata['subbasin_masks'].split(RHESSysMetadata.VALUE_DELIM)
        for mask in masks:
            result = self.grassLib.script.run_command('r.mask', flags='o', input=mask, maskcats='1',
                                                      quiet=True)
            if result != 0:
                raise RunException("r.mask failed to set mask to sub-basin {0}, returning {1}".format(mask,
                                                                                                      result))
            # Run CF
            p = self.grassLib.script.pipe_command(cfPath, out=flowOutpath.format(mask=mask), 
                                                  template=templatePath, dem=demRast, 
                                                  slope=self.grassMetadata['slope_rast'],
                                                  stream=self.grassMetadata['streams_rast'],
                                                  road=roads, roof=roofs, impervious=impervious,
                                                  cellsize=demResX)
            (pStdout, pStderr) = p.communicate()
            
            if verbose:
                self.outfp.write("CF output:\n")
                self.outfp.write(pStdout)
                if pStderr:
                    self.outfp.write(pStderr)
            
            if p.returncode != 0:
                raise RunException("createflowpaths failed, returning %s" % ( str(p.returncode),))
            
            # Write cf output to project directory
            cfOut = open(cfOutpath.format(mask=mask), 'w')
            cfOut.write(pStdout)
            if pStderr:
                cfOut.write("\n\nStandard error output:\n\n")
                cfOut.write(pStderr)
            cfOut.close()
            
            surfFlow = os.path.join(self.paths.RHESSYS_FLOW, surfaceFlowtableTemplate.format(mask=mask))
            surfaceFlowtables.append(surfFlow)
            subsurfFlow = os.path.join(self.paths.RHESSYS_FLOW, subsurfaceFlowtableTemplate.format(mask=mask))
            subsurfaceFlowtables.append(subsurfFlow)
        
        # Remove mask
        result = self.grassLib.script.run_command('r.mask', flags='r', quiet=True)
        if result != 0:
            raise RunException("r.mask failed to remove mask") 
            
        # Write metadata
        cfCmd = "%s out=%s template=%s dem=%s slope=%s stream=%s road=%s roof=%s impervious=%s cellsize=%s" % \
        (cfPath, flowOutpath, templatePath, demRast, self.grassMetadata['slope_rast'],
         self.grassMetadata['streams_rast'], roads, roofs, impervious, demResX)
        RHESSysMetadata.writeRHESSysEntry(self.context, 'flowtable_cmd', cfCmd)
        RHESSysMetadata.writeRHESSysEntry(self.context, 'surface_flowtables', 
                                          RHESSysMetadata.VALUE_DELIM.join([self.paths.relpath(s) for s in surfaceFlowtables]) )
        RHESSysMetadata.writeRHESSysEntry(self.context, 'subsurface_flowtables', 
                                          RHESSysMetadata.VALUE_DELIM.join([self.paths.relpath(s) for s in subsurfaceFlowtables]) )

        if verbose:
            self.outfp.write('\n\nFinished creating flow tables\n')
            
        # Write processing history
        RHESSysMetadata.appendProcessingHistoryItem(self.context, RHESSysMetadata.getCommandLine())
         