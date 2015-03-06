"""@package rhessysworkflows.command.worldfile
    
@brief RHESSysWorkflows commands related to world files

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

class WorldfileMultiple(GrassCommand):
    
    def __init__(self, projectDir, configFile=None, outfp=sys.stdout):
        """ Construct a WorldfileMultiple command.
        Arguments:
        projectDir -- string    The path to the project directory
        configFile -- string    The path to an EcohydroLib configuration file
        outfp -- file-like object    Where output should be written to
        
        """
        super(WorldfileMultiple, self).__init__(projectDir, configFile, outfp)
    
    def checkMetadata(self):
        """ Check to make sure the project directory has the necessary metadata to run this command.
        """
        super(WorldfileMultiple, self).checkMetadata()
        
        # Check for necessary information in metadata
        if not 'basin_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a basin raster in a GRASS mapset" % (self.context.projectDir,))
        if not 'subbasins_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a sub-basin raster in a GRASS mapset" % (self.context.projectDir,))
        if not 'dem_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a DEM raster in a GRASS mapset" % (self.context.projectDir,)) 
        if not 'soil_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a soil raster in a GRASS mapset" % (self.context.projectDir,))
        if not 'patch_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a patch raster in a GRASS mapset" % (self.context.projectDir,))
        
        if not 'rhessys_dir' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a RHESSys directory" % (self.context.projectDir,))
        if not 'g2w_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a grass2world executable" % (self.context.projectDir,))
        if not 'rat_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain an AverageTables executable" % (self.context.projectDir,))
        if not 'template' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a world template" % (self.context.projectDir,))
        if not 'rhessys_dir' in self.metadata:
            raise MetadataException("Metadata in project directory {0} does not contain a RHESSys directory".format(self.context.projectDir))
            
    
    def run(self, *args, **kwargs):
        """ Multiple worldfiles, one worldfile for each subbasin delineated. 
        
        Arguments:
        verbose -- boolean    Produce verbose output. Default: False.
        """
        verbose = kwargs.get('verbose', False)
        
        self.checkMetadata()
        
        rhessysDir = self.metadata['rhessys_dir']
        self.paths = RHESSysPaths(self.context.projectDir, rhessysDir)
        
        templateFilename = os.path.basename(self.metadata['template'])
        templateFilepath = os.path.join(self.context.projectDir, self.metadata['template'])
        
        g2wPath = os.path.join(self.context.projectDir, self.metadata['g2w_bin'])
        
        # Make sure g2w can find rat
        g2wEnv = dict(os.environ)
        g2wEnv['PATH'] = self.paths.RHESSYS_BIN + os.pathsep + g2wEnv['PATH']
        
        # Make sure region is properly set
        demRast = self.grassMetadata['dem_rast']
        result = self.grassLib.script.run_command('g.region', rast=demRast)
        if result != 0:
            raise RunException("g.region failed to set region to DEM, returning {0}".format(result))
        
        # Mask subbasin to basin
        basin_rast = self.grassMetadata['basin_rast']
        result = self.grassLib.script.run_command('r.mask', flags='o', input=basin_rast, maskcats='1',
                                                  quiet=True)
        if result != 0:
            sys.exit("r.mask failed to set mask to basin, returning %s" % (result,))
        subbasin_raster = self.grassMetadata['subbasins_rast']
        subbasin_mask = "{0}_mask".format(subbasin_raster)
        mapcalc_input = "{subbasin_mask}={subbasins}".format(subbasin_mask=subbasin_mask,
                                                             subbasins=subbasin_raster)
        result = self.grassLib.script.write_command('r.mapcalc',
                                                    stdin=mapcalc_input,
                                                    stdout=PIPE,
                                                    stderr=PIPE)
        if result != 0:
            raise RunException("r.mapcalc failed to generate masked subbasin map {0}, input: {1}".format(subbasin_raster,
                                                                                                         mapcalc_input))
        
        # Get list of subbasins
        result = self.grassLib.script.read_command('r.stats', flags='n', input=subbasin_raster, quiet=True)
        if result is None or result == '':
            raise RunException("Error reading subbasin map {0}".format(subbasin_raster))
             
        subbasins = result.split()
        subbasin_masks = []
        worldfiles = []
        for subbasin in subbasins:
            # Remove mask
            result = self.grassLib.script.run_command('r.mask', flags='r', quiet=True)
            if result != 0:
                raise RunException("r.mask failed to remove mask")
            
            # Make a mask layer for the sub-basin
            mask_name = "subbasin_{0}".format(subbasin)
            subbasin_masks.append(mask_name)
            result = self.grassLib.script.write_command('r.mapcalc',
                                                        stdin="{mask_name}={subbasins} == {subbasin_number}".format(mask_name=mask_name,
                                                                                                                    subbasins=subbasin_mask,
                                                                                                                    subbasin_number=subbasin),
                                                        stdout=PIPE,
                                                        stderr=PIPE)
            if result != 0:
                raise RunException("r.mapcalc failed to generate mask for subbasin {0}".format(subbasin))
        
            # Mask to the sub-basin
            result = self.grassLib.script.run_command('r.mask', flags='o', input=mask_name, maskcats='1',
                                                      quiet=True)
            if result != 0:
                raise RunException("r.mask failed to set mask to sub-basin {0}, returning {1}".format(mask_name,
                                                                                                      result))
         
            worldfileName = "world_subbasin_{0}_init".format(subbasin)
            worldfilePath = os.path.join(self.paths.RHESSYS_WORLD, worldfileName)
            worldfiles.append(worldfilePath)
            g2wCommand = "{g2w} -t {template} -w {worldfile}".format(g2w=g2wPath, 
                                                                     template=templateFilepath, 
                                                                     worldfile=worldfilePath)
            
            if verbose:
                self.outfp.write("{0}\n".format(g2wCommand))
                self.outfp.write("\nRunning grass2world from {0}...".format(self.paths.RHESSYS_BIN))
                self.outfp.flush()

            cmdArgs = g2wCommand.split()
            process = Popen(cmdArgs, cwd=self.paths.RHESSYS_BIN, env=g2wEnv, 
                            stdout=PIPE, stderr=PIPE)
            (process_stdout, process_stderr) = process.communicate()
            if process.returncode != 0:
                raise RunException("grass2world failed, returning {0}".format(process.returncode))
     
            if verbose:
                self.outfp.write(process_stdout)
                self.outfp.write(process_stderr)
         
        # Remove mask
        result = self.grassLib.script.run_command('r.mask', flags='r', quiet=True)
        if result != 0:
            raise RunException("r.mask failed to remove mask") 
         
        # Write metadata
        RHESSysMetadata.writeRHESSysEntry(self.context, 'worldfiles_init', 
                                          RHESSysMetadata.VALUE_DELIM.join([self.paths.relpath(w) for w in worldfiles]))
        RHESSysMetadata.writeRHESSysEntry(self.context, 'subbasin_masks', 
                                          RHESSysMetadata.VALUE_DELIM.join([m for m in subbasin_masks]))

        if verbose:
            self.outfp.write('\n\nFinished creating worldfiles\n')

        # Write processing history
        RHESSysMetadata.appendProcessingHistoryItem(self.context, RHESSysMetadata.getCommandLine())
