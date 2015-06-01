#!/usr/bin/env python
"""@package PatchToMovie

@brief Tool for making animations of patch-scale RHESSys output variables.

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2014, University of North Carolina at Chapel Hill
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


Pre conditions
--------------
1. Configuration file must define the following sections and values:
   'GRASS', 'GISBASE'
   'RHESSYS', 'PATH_OF_FFMPEG'

2. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   grass_dbase
   grass_location
   grass_mapset


Post conditions
---------------
None
   
"""
import os, sys, shutil, tempfile, re
import subprocess, shlex
import time, random
import argparse
import operator

import numpy as np

from ecohydrolib.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from ecohydrolib.grasslib import *

from rhessysworkflows.rhessys import RHESSysOutput

PATCH_DAILY_RE = re.compile('^(.+_patch.daily)$')
VARIABLE_EXPR_RE = re.compile(r'\b([a-zA-z]\w+)\b')
RECLASS_MAP_TMP = "patchtomovietmp_%d" % (random.randint(100000, 999999),)

MPEG4_CODEC = 'mpeg4'
H264_CODEC = 'libx264'
DEFAULT_CODEC = MPEG4_CODEC
CODECS = [MPEG4_CODEC, H264_CODEC]

# Handle command line options
parser = argparse.ArgumentParser(description='Generate movie from patch level daily RHESSys output')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file.')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-d', '--rhessysOutFile', required=True,
                    help='Directory containing RHESSys patch output, specificically patch daily output stored in a file whose name ends with "_patch.daily".')
parser.add_argument('--mask', required=False, default=None,
                    help='Name of raster to use as a mask')
parser.add_argument('--overlay', required=False, default=None, nargs='*',
                    help='Name of raster map to use as overlay')
parser.add_argument('--overlayLegend', required=False, default=False,
                    help='Display legend for overlay layer. If more than one overlay is present, will only draw legend for the first.')
parser.add_argument('-o', '--outputDir', required=True,
                    help='Directory to which movie should be output')
parser.add_argument('-f', '--outputFile', required=True,
                    help='Name of file to store movie in; .mp4 extension will be added.  If file exists it will be overwritten.')
parser.add_argument('--patchMap', required=False, default='patch',
                    help='Name of patch map')
parser.add_argument('-v', '--outputVariable', required=True,
                    help='Name of RHESSys variable to be mapped.  Can be an expression such as "trans_sat + trans_unsat"')
parser.add_argument('-t' ,'--mapTitle', required=False,
                    help='Text to use for title.  If not supplied, variable name will be used')
parser.add_argument('-u', '--variableUnit', required=False, default='mm',
                    help='Units of variable, which will be displayed in paranthesis next to the variable name on the map')
parser.add_argument('--fps', required=False, type=int, default=15,
                    help='Frames per second of output video')
parser.add_argument('--codec', required=False, default=DEFAULT_CODEC, choices=CODECS,
                    help="Video codec to use. Default: %s" % (DEFAULT_CODEC,) )
parser.add_argument('--rescale', required=False, type=float,
                    help='Rescale raster values of 0 to args.resample to 0 to 255 in output images.')
args = parser.parse_args()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile)

ffmpegPath = context.config.get('RHESSYS', 'PATH_OF_FFMPEG')

# Check for necessary information in metadata
metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'grass_dbase' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS Dbase" % (context.projectDir,)) 
if not 'grass_location' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS location" % (context.projectDir,)) 
if not 'grass_mapset' in metadata:
    sys.exit("Metadata in project directory %s does not contain a GRASS mapset" % (context.projectDir,))

if not os.path.isfile(args.rhessysOutFile) or not os.access(args.rhessysOutFile, os.R_OK):
    sys.exit("Unable to read RHESSys output file %s" % (args.rhessysOutFile,))
patchDailyFilepath = os.path.abspath(args.rhessysOutFile) 

if not os.path.isdir(args.outputDir) or not os.access(args.outputDir, os.W_OK):
    sys.exit("Unable to write to output directory %s" % (args.outputDir,) )
outputDir = os.path.abspath(args.outputDir)
outputFile = "%s.mp4" % (args.outputFile)
outputFilePath = os.path.join(outputDir, outputFile)

# Determine output variables
variables = ['patchID']
m = VARIABLE_EXPR_RE.findall(args.outputVariable)
if m:
    variables += m
else:
    sys.exit("No output variables specified")

title = args.outputVariable
if args.mapTitle:
    title = args.mapTitle  
if not args.rescale:
    title += ' (' + args.variableUnit + ')'
  
if not os.path.isfile(patchDailyFilepath) or not os.access(patchDailyFilepath, os.R_OK):
    sys.exit("Unable to read RHESSys patch daily output file %s" % (patchDailyFilepath,))

# 1. Get tmp folder for temprarily storing images 
tmpDir = tempfile.mkdtemp()
print("Temp dir: %s" % (tmpDir,) )
reclassRule = os.path.join(tmpDir, 'reclass.rule')

# 2. Initialize GRASS
grassDbase = os.path.join(context.projectDir, metadata['grass_dbase'])
grassConfig = GRASSConfig(context, grassDbase, metadata['grass_location'], metadata['grass_mapset'])
grassLib = GRASSLib(grassConfig=grassConfig)

# Set mask (if present)
if args.mask:
    result = grassLib.script.run_command('r.mask',
                                         input=args.mask,
                                         maskcats="1",
                                         flags="o")
    if result != 0:
        sys.exit("Failed to set mask using layer %s" % (args.mask,) )
    # Zoom to map extent
    result = grassLib.script.run_command('g.region',
                                         rast='MASK',
                                         zoom='MASK')
    if result != 0:
        sys.exit("Failed to set region to layer %s" % \
                 (args.mask,) )
        
# Set environment variables for GRASS PNG output driver
os.environ['GRASS_RENDER_IMMEDIATE'] = 'FALSE'
os.environ['GRASS_TRUECOLOR'] = 'TRUE'
os.environ['GRASS_WIDTH'] = '960'
os.environ['GRASS_HEIGHT'] = '720'

# 3. Open file ending in "patch.daily" in rhessys output dir
print("Reading RHESSys output data (this may take a while)...")
f = open(patchDailyFilepath)
data = RHESSysOutput.readColumnsFromPatchDailyFile(f, variables)
f.close()
if len(data) < 1:
    sys.exit("No data found for variable in RHESSys output file '%s'" % \
             (patchDailyFilepath,) )

# 4. For each day
for (i, key) in enumerate(data):
    dateStr = "%d/%d/%d" % (key.month, key.day, key.year)
    # Set filename env for PNG driver
    imageFilename = "%s%04d.png" % (RECLASS_MAP_TMP, i+1 )
    reclassImagePath = os.path.join(tmpDir, imageFilename)
    os.environ['GRASS_PNGFILE'] = reclassImagePath
    
    dataForDate = data[key]
    # a. Write reclass rule to temp file
    reclass = open(reclassRule, 'w')
    
    patchIDs = [ int(f) for f in dataForDate['patchID'] ]
    # Could do this outside the loop, but want to make sure it's near declaration of 
    # dataForDate
    expr = VARIABLE_EXPR_RE.sub(r'np.array(dataForDate["\1"])', args.outputVariable)
    variable = eval(expr)
      
    for (j, var) in enumerate(variable):
        #reclass.write("%d = %f\n" % (patchIDs[j], var) )
        reclass.write("%d:%d:%f:%f\n" % (patchIDs[j], patchIDs[j], var, var) )
    reclass.close()
    
    # b. Generate temporary map for variable
    result = grassLib.script.run_command('r.recode', 
                                         input=args.patchMap, 
                                         output=RECLASS_MAP_TMP,
                                         rules=reclassRule,
                                         overwrite=True)
    if result != 0:
        sys.exit("Failed to create reclass map for date %s" % (dateStr,) )
        
    tmpMap = RECLASS_MAP_TMP
    if args.rescale:
        tmpMap = "%s_rescale" % (RECLASS_MAP_TMP,)
        fromScale = "0,%d" % (args.rescale,)
        rRescaleOptions = {'input': RECLASS_MAP_TMP,
                           'output': tmpMap,
                           'from': fromScale,
                           'to': '0,255',
                           'overwrite': True}
        result = grassLib.script.run_command('r.rescale', 
                                             **rRescaleOptions)
        if result != 0:
            sys.exit("Failed to rescale map when rendering image %s" % (imageFilename,) )
    # c. Render map with annotations to PNG image

    # Start a new PNG driver
    result = grassLib.script.run_command('d.mon', start='PNG')
    if result != 0:
        sys.exit("Failed to start PNG driver while rendering image %s" % \
                 (imageFilename,) )
    
    # Render image
    result = grassLib.script.run_command('d.rast',
                                         map=tmpMap)
    if result != 0:
        sys.exit("Failed to render map %s while rendering image %s" % \
                 (tmpMap, imageFilename) )
       
    # Draw overlays 
    if args.overlay:
        for (i, overlay) in enumerate(args.overlay):
            result = grassLib.script.run_command('d.rast',
                                                 map=overlay,
                                                 flags='o')
            if result != 0:
                sys.exit("Failed to draw overlay map %s while rendering image %s" % \
                         (overlay, imageFilename) )
            if i == 0 and args.overlayLegend:
                # Add legend for overlay
                result = grassLib.script.run_command('d.legend',
                                                 map=overlay,
                                                 at='15,50,10,15')
                if result != 0:
                    sys.exit("Failed to add legend for overlay map %s while rendering image %s" % \
                             (args.overlay, imageFilename) )
                # Write name of overlay layer
                result = grassLib.script.run_command('d.text',
                                                 text=overlay,
                                                 size=2.5,
                                                 color='black',
                                                 at='12, 12',
                                                 align='cc')
                if result != 0:
                    sys.exit("Failed to add overlay annotation to map while rendering image %s" % \
                             (imageFilename,) )
            
    # Add annotations
    result = grassLib.script.run_command('d.legend',
                                         map=tmpMap,
                                         at='63,88,77,87')
    if result != 0:
        sys.exit("Failed to add legend to map while rendering image %s" % \
                 (imageFilename,) )
    
    # Set high
    if args.rescale:
        result = grassLib.script.run_command('d.text',
                                             text='High',
                                             size=5,
                                             color='black',
                                             at='90,61',
                                             align='cc')
        if result != 0:
            sys.exit("Failed to high scale legend to map while rendering image %s" % \
                     (imageFilename,) )
        
    # Set low
    if args.rescale:
        result = grassLib.script.run_command('d.text',
                                             text='Low',
                                             size=5,
                                             color='black',
                                             at='88,91',
                                             align='cc')
        if result != 0:
            sys.exit("Failed to add low scale legend to map while rendering image %s" % \
                     (imageFilename,) )
    
    # Set title
    result = grassLib.script.run_command('d.text',
                                         text=title,
                                         size=5,
                                         color='black',
                                         at='73,98',
                                         align='cc')
    if result != 0:
        sys.exit("Failed to add title to map while rendering image %s" % \
                 (imageFilename,) )
    
    # Write date
    result = grassLib.script.run_command('d.text',
                                         text=dateStr,
                                         size=5,
                                         color='black',
                                         at='12,98',
                                         align='cc')
    if result != 0:
        sys.exit("Failed to add date to map while rendering image %s" % \
                 (imageFilename,) )
        
    # Close the PNG driver, writing PNG image
    result = grassLib.script.run_command('d.mon', stop='PNG')
    if result != 0:
        sys.exit("Error occured when closing PNG driver for image %s" % \
                 (imageFilename,) )
    
# 5. Combine images to ffmpeg movie of specified name in specified location  
# Documentation: https://trac.ffmpeg.org/wiki/Create%20a%20video%20slideshow%20from%20images
# e.g. ffmpeg -r 1/5 -i img%03d.png -vcodec libx264 -r 30 -pix_fmt yuv420p out.mp4
cmd = "%s -y -r %d -i %s%%04d.png -vcodec %s -pix_fmt yuv420p %s" % (ffmpegPath, args.fps, RECLASS_MAP_TMP, args.codec, outputFilePath)
# print(cmd)
cmdArray = shlex.split(cmd)
p = subprocess.Popen(cmdArray, cwd=tmpDir)
result = p.wait()
if result != 0:
    sys.exit("Error %d encountered when creating movie using ffmpeg.  Command line was:\n%s\n" % \
             (result, cmd) )

# Cleanup
shutil.rmtree(tmpDir)
if args.rescale:
    result = grassLib.script.run_command('g.remove', rast=tmpMap)
    if result != 0:
        sys.exit("Failed to remove temporary map %s" % (tmpMap,) )
result = grassLib.script.run_command('g.remove', rast=RECLASS_MAP_TMP)
if result != 0:
    sys.exit("Failed to remove temporary map %s" % (RECLASS_MAP_TMP,) )
