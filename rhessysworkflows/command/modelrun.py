"""@package rhessysworkflows.command.modelrun
    
@brief RHESSysWorkflows commands related to running RHESSys models

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
import datetime
import shutil

from rhessysworkflows.command.base import GrassCommand
from rhessysworkflows.command.exceptions import MetadataException
from rhessysworkflows.command.exceptions import RunException

from rhessysworkflows.rhessys import RHESSysPaths
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import datetimeToString
from rhessysworkflows.rhessys import generateCommandString
from rhessysworkflows.worldfileio import getClimateBaseStationFilenames
from rhessysworkflows.climateio import getStartAndEndDateForClimateStation

class LAIReadMultiple(GrassCommand):
    def __init__(self, projectDir, configFile=None, outfp=sys.stdout):
        """ Construct a LAIReadMultiple command.
        Arguments:
        projectDir -- string    The path to the project directory
        configFile -- string    The path to an EcohydroLib configuration file
        outfp -- file-like object    Where output should be written to
        
        """
        super(LAIReadMultiple, self).__init__(projectDir, configFile, outfp)
        
    def checkMetadata(self, *args, **kwargs):
        """ Check to make sure the project directory has the necessary metadata to run this command.
        """
        super(LAIReadMultiple, self).checkMetadata()
        
        # Check for necessary information in self.metadata
        if not 'subbasin_masks' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain multiple worldfile masks" % (self.context.projectDir,))
        if not 'dem_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a DEM raster" % (self.context.projectDir,))
        if not 'hillslope_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a hillslope raster" % (self.context.projectDir,))  
        if not 'zone_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a zone raster" % (self.context.projectDir,)) 
        if not 'patch_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a patch raster" % (self.context.projectDir,)) 
        if not 'stratum_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with a stratum raster" % (self.context.projectDir,)) 
        if not 'lai_rast' in self.grassMetadata:
            raise MetadataException("Metadata in project directory %s does not contain a GRASS dataset with an LAI raster" % (self.context.projectDir,)) 
        
        if not 'rhessys_dir' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a RHESSys directory" % (self.context.projectDir,))
        if not 'rhessys_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a RHESSys binary" % (self.context.projectDir,))
        if not 'lairead_bin' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain a lairead executable" % (self.context.projectDir,))
        if not 'worldfiles_init' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain initial worldfiles" % (self.context.projectDir,))
        if not 'allometric_table' in self.metadata:
            raise MetadataException("Metadata in project directory %s does not contain an allometric table" % (self.context.projectDir,))
        
        topmodel = kwargs.get('topmodel', False)
        if not topmodel:
            if not 'surface_flowtables' in self.metadata:
                raise MetadataException("Metadata in project directory %s does not contain surface flowtables" % (self.context.projectDir,))
            if not 'subsurface_flowtables' in self.metadata:
                raise MetadataException("Metadata in project directory %s does not contain a subsurface flowtables" % (self.context.projectDir,))
        
    def run(self, *args, **kwargs):
        """ Run lairead for multiple worldfiles 
        
        Arguments:
        topmodel -- boolean   Whether to run RHESSys in TOPMODEL model. Default: False.
        verbose -- boolean    Produce verbose output. Default: False.
        """
        verbose = kwargs.get('verbose', False)
        topmodel = kwargs.get('topmodel', False)
        
        self.checkMetadata(topmodel=topmodel)
        
        rhessysDir = self.metadata['rhessys_dir']
        self.paths = RHESSysPaths(self.context.projectDir, rhessysDir)
        rhessysBinPath = os.path.join(self.context.projectDir, self.metadata['rhessys_bin'])
        
        # Make sure region is properly set
        demRast = self.grassMetadata['dem_rast']
        result = self.grassLib.script.run_command('g.region', rast=demRast)
        if result != 0:
            raise RunException("g.region failed to set region to DEM, returning {0}".format(result))
        
        # Run lairead for each worldfile
        lairead_tecfiles = []
        final_worldfiles = []
        worldfiles = self.metadata['worldfiles_init'].split(RHESSysMetadata.VALUE_DELIM)
        masks = self.metadata['subbasin_masks'].split(RHESSysMetadata.VALUE_DELIM)
        
        surfaceFlowtables = subsurfaceFlowtables = None
        if not topmodel:
            surfaceFlowtables = self.metadata['surface_flowtables'].split(RHESSysMetadata.VALUE_DELIM)
            subsurfaceFlowtables = self.metadata['subsurface_flowtables'].split(RHESSysMetadata.VALUE_DELIM)
        
        for (i, worldfile) in enumerate(worldfiles):
            worldfilePath = os.path.join(self.context.projectDir, worldfile)
            worldfileDir = os.path.dirname(worldfilePath)
            
            surfaceFlowtable = subsurfaceFlowtable = None
            if not topmodel:
                surfaceFlowtable = surfaceFlowtables[i] # Assumption: worldfiles and flowtables lists are in the same order
                subsurfaceFlowtable = subsurfaceFlowtables[i] # Assumption: worldfiles and flowtables lists are in the same order
                
            # Mask to correct mask
            mask = masks[i] # Assumption: worldfiles and masks lists are in the same order
            result = self.grassLib.script.run_command('r.mask', flags='o', input=mask, maskcats='1',
                                                      quiet=True)
            if result != 0:
                raise RunException("r.mask failed to set mask to sub-basin {0}, returning {1}".format(mask,
                                                                                                      result))
            ## 1. Determine legal simulation start and date from climate data 
            # Read first climate station from worldfile
            header = "{0}.hdr".format(worldfile)
            headerPath = os.path.join(self.context.projectDir, header)
            stations = getClimateBaseStationFilenames(headerPath)
            if not len(stations) > 0:
                raise RunException("No climate stations found in worldfile header {0}".format(headerPath))
            firstStationPath = os.path.normpath( os.path.join(self.paths.RHESSYS_DIR, stations[0]) )
            if verbose:
                self.outfp.write("First climate station in worldfile: %s\n" % (firstStationPath,) )
            
            # Read climate timeseries for start and end date, write to metadata
            (startDate, endDate) = getStartAndEndDateForClimateStation(firstStationPath, self.paths)
            if verbose:
                self.outfp.write("start date: %s, end date: %s\n" % ( str(startDate), str(endDate) ) )
            fourDays = datetime.timedelta(days=4)
            if endDate - startDate < fourDays:
                raise RunException("Climate time-series defined by station %s is too short to run lairead (less than four-days long)" %
                                   (firstStationPath,) )
            
            ## 2. Run LAI read to generate redefine worldfile
            tecDurRedef = datetime.timedelta(days=1)
            tecRedef = startDate + tecDurRedef
            laireadPath = os.path.join(self.context.projectDir, self.metadata['lairead_bin'])
            oldWorldPath = os.path.join(self.context.projectDir, worldfile)
            redefWorldName = "%s.Y%dM%dD%dH%d" % \
                (worldfile, tecRedef.year, tecRedef.month, tecRedef.day, tecRedef.hour)
            redefWorldPath = os.path.join(self.context.projectDir, redefWorldName)
            allomPath = os.path.join(self.context.projectDir, self.metadata['allometric_table'])
            
            if verbose:
                self.outfp.write("\nRunning lairead for subbasin {0}...".format(mask))
                
            p = self.grassLib.script.pipe_command(laireadPath, old=oldWorldPath, redef=redefWorldPath,
                                                  allom=allomPath, lai=self.grassMetadata['lai_rast'],
                                                  vegid=self.grassMetadata['stratum_rast'],
                                                  zone=self.grassMetadata['zone_rast'],
                                                  hill=self.grassMetadata['hillslope_rast'],
                                                  patch=self.grassMetadata['patch_rast'],
                                                  mask=mask)
            (stdoutStr, stderrStr) = p.communicate() 
            result = p.returncode
            if result != 0:
                self.outfp.write(stdoutStr)
                raise RunException("\nlairead failed, returning %s" % (result,))
            
            if verbose:
                self.outfp.write('done\n')
                        
            ## 3. Write TEC file for redefining the initial flow table
            ##    Redefine on the second day of the simulation, write output
            ##    on the third day
            tecName = "tec.lairead_{0}".format(mask)
            tecPath = os.path.join(self.paths.RHESSYS_TEC, tecName)
            tecDurOutput = datetime.timedelta(days=2)
            tecOutput = startDate + tecDurOutput
            
            f = open(tecPath, 'w')
            f.write("%s redefine_world%s" % 
                    (datetimeToString(tecRedef), os.linesep) )
            f.write("%s output_current_state%s" %
                    (datetimeToString(tecOutput), os.linesep) )
            f.close()
            lairead_tecfiles.append(tecPath)
            
            ## 4. Run RHESSys for the first 4 legal days with redefine TEC
            rhessysStart = startDate
            rhessysDur = datetime.timedelta(days=3)
            rhessysEnd = startDate + rhessysDur
            surfaceFlowtablePath = subSurfaceFlowtablePath = None
            if not topmodel:
                surfaceFlowtablePath = os.path.join(self.context.projectDir, surfaceFlowtable)
                subsurfaceFlowtablePath = os.path.join(self.context.projectDir, subsurfaceFlowtable)
            
            rhessysCmd = generateCommandString(rhessysBinPath, None,
                                               rhessysStart, rhessysEnd,
                                               tecPath, oldWorldPath,
                                               surfaceFlowtablePath, subsurfaceFlowtablePath)
            if verbose:
                self.outfp.write('\nRunning RHESSys to redefine worldfile with vegetation carbon stores...\n')
                self.outfp.write(rhessysCmd)
                self.outfp.write('\n')
            
            cmdArgs = rhessysCmd.split()
            process = Popen(cmdArgs, cwd=self.paths.RHESSYS_DIR, stdout=PIPE, stderr=PIPE)
            (process_stdout, process_stderr) = process.communicate()
            if verbose:
                self.outfp.write(process_stdout)
                self.outfp.write(process_stderr)
            if process.returncode != 0:
                raise RunException("\n\nRHESSys failed, returning %s" % (process.returncode,) )
            
            if verbose:    
                sys.stdout.write('done\n')
                
            ## 5. Rename redefine worldfile, write to metadata
            outputWorldName = "%s.Y%dM%dD%dH%d.state" % \
                (worldfile, tecOutput.year, tecOutput.month, tecOutput.day, tecOutput.hour)
            outputWorldPath = os.path.join(self.context.projectDir, outputWorldName)
            
            if not os.access(outputWorldPath, os.W_OK):
                raise RunException("Unable to find redefined worldfile %s" % (outputWorldPath,) )
                
            newWorldName = "world_{0}".format(mask)
            newWorldPath = os.path.join(self.paths.RHESSYS_WORLD, newWorldName)
            
            shutil.move(outputWorldPath, newWorldPath)
            if not os.path.exists(newWorldPath):
                raise RunException("Failed to copy redefined worldfile %s to %s" % (outputWorldPath, newWorldPath) )
            
            final_worldfiles.append(newWorldPath)
            
            # Copy world file header from init worldfile to final world file
            newHeader = "%s.hdr" % (newWorldName,)
            newHeaderPath = os.path.join(self.paths.RHESSYS_WORLD, newHeader)
            shutil.copyfile(headerPath, newHeaderPath)
            
        if verbose:    
            sys.stdout.write('\n\nSuccessfully used lairead to initialize vegetation carbon stores.\n')
        
        # Write metadata    
        RHESSysMetadata.writeRHESSysEntry(self.context, 'worldfiles',
                                          RHESSysMetadata.VALUE_DELIM.join([self.paths.relpath(w) for w in final_worldfiles]))
        RHESSysMetadata.writeRHESSysEntry(self.context, 'lairead_tecfiles', 
                                          RHESSysMetadata.VALUE_DELIM.join([self.paths.relpath(t) for t in lairead_tecfiles]))
        RHESSysMetadata.writeRHESSysEntry(self.context, 'lairead_mode_topmodel', str(topmodel))
            
        # Write processing history
        RHESSysMetadata.appendProcessingHistoryItem(self.context, RHESSysMetadata.getCommandLine())