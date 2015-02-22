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
import sys

from rhessysworkflows.command.base import GrassCommand
from rhessysworkflows.command.exceptions import MetadataException
from rhessysworkflows.command.exceptions import RunException

from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.metadata import RHESSysMetadata

class WorldfileMultiple(GrassCommand):
    
    def __init__(self, projectDir, configFile=None, outfp=sys.stdout):
        super(WorldfileMultiple, self).__init__(projectDir, configFile, outfp)
    
    def checkMetadata(self):
        super(WorldfileMultiple, self).checkMetadata()
        
        # Check for necessary information in metadata
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
        self.checkMetadata()
        rhessysDir = self.metadata['rhessys_dir']
        self.paths = RHESSysPaths(self.context.projectDir, rhessysDir)
        
        self.setupGrassEnv()
        
        verbose = kwargs.get('verbose', False)
        
        ## Run grass2world
        # Make sure mask and region are properly set
        demRast = self.grassMetadata['dem_rast']
        result = self.grassLib.script.run_command('g.region', rast=demRast)
        if result != 0:
            sys.exit("g.region failed to set region to DEM, returning %s" % (result,))
        
        basinRast = self.grassMetadata['basin_rast']
        result = self.grassLib.script.run_command('r.mask', flags='o', input=basinRast, maskcats='1')
        if result != 0:
            sys.exit("r.mask failed to set mask to basin, returning %s" % (result,))
        
        templateFilename = os.path.basename(self.metadata['template'])
        templateFilepath = os.path.join(context.projectDir, metadata['template'])
        
        worldfileName = "%s_init" % (templateFilename.replace('template', 'world'), )
        worldfilePath = os.path.join(self.paths.RHESSYS_WORLD, worldfileName)
        
        g2wPath = os.path.join(self.context.projectDir, self.metadata['g2w_bin'])
        g2wCommand = "%s -t %s -w %s" % (g2wPath, templateFilepath, worldfilePath)
        
        # Make sure g2w can find rat
        g2wEnv = dict(os.environ)
        g2wEnv['PATH'] = self.paths.RHESSYS_BIN + os.pathsep + g2wEnv['PATH']
        
        if verbose:
            self.outfp.write("{0}\n".format(g2wCommand))
        
        self.outfp.write("\nRunning grass2world from %s..." % (self.paths.RHESSYS_BIN,) )
        self.outfp.flush()
        cmdArgs = g2wCommand.split()
        process = Popen(cmdArgs, cwd=self.paths.RHESSYS_BIN, env=g2wEnv, 
                        stdout=PIPE, stderr=PIPE)
        (process_stdout, process_stderr) = process.communicate()
        
        if verbose:
            self.outfp.write(process_stdout)
            self.outfp.write(process_stderr)
        
        if process.returncode != 0:
            raise RunException("grass2world failed, returning {0}".format(process.returncode))
        
        # Write metadata
        RHESSysMetadata.writeRHESSysEntry(context, 'worldfile_zero', self.paths.relpath(worldfilePath) )

        self.outfp.write('\n\nFinished creating worldfile\n')

        # Write processing history
        RHESSysMetadata.appendProcessingHistoryItem(self.context, RHESSysMetadata.getCommandLine())
