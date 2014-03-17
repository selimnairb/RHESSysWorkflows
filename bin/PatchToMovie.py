#!/usr/bin/env python
"""
    Args: 
        - rhessys output dir
        - GRASSdata path
        - location of output movie
        - name of output movie
        - variable to output

"""
import os, sys, shutil, tempfile, re
import subprocess, shlex
import time, random
import argparse
import operator

import numpy as np

from ecohydrolib.context import Context
from ecohydrolib.grasslib import *

from rhessyscalibrator.postprocess import RHESSysCalibratorPostprocess

FFMPEG_PATH = '/usr/local/bin/ffmpeg'
PATCH_DAILY_RE = re.compile('^(.+_patch.daily)$')
VARIABLE_EXPR_RE = re.compile(r'\b([a-zA-z]\w+)\b')
RECLASS_MAP_TMP = "patchtomovietmp_%d" % (random.randint(100000, 999999),)

# Handle command line options
parser = argparse.ArgumentParser(description='Generate movie from patch level daily RHESSys output')
parser.add_argument('-r', '--rhessysOutFile', required=True,
                    help='Directory containing RHESSys patch output, specificically patch daily output stored in a file whose name ends with "_patch.daily".')
parser.add_argument('-g', '--grassDbase', required=True,
                    help='GRASS DBase directory')
parser.add_argument('-l', '--grassLocation', required=False, default='default',
                    help='GRASS location')
parser.add_argument('-m', '--grassMapset', required=False, default='PERMANENT',
                    help='GRASS mapset')
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
parser.add_argument('-p', '--patchMap', required=False, default='patch',
                    help='Name of patch map')
parser.add_argument('-v', '--outputVariable', required=True,
                    help='Name of RHESSys variable to be mapped.  Can be an expression such as "trans_sat + trans_unsat"')
parser.add_argument('-t' ,'--mapTitle', required=False,
                    help='Text to use for title.  If not supplied, variable name will be used')
parser.add_argument('-u', '--variableUnit', required=False, default='mm',
                    help='Units of variable, which will be displayed in paranthesis next to the variable name on the map')
parser.add_argument('--fps', required=False, type=int, default=15,
                    help='Frames per second of output video')
parser.add_argument('--rescale', required=False, type=float,
                    help='Rescale raster values of 0 to args.resample to 0 to 255 in output images.')
group = parser.add_mutually_exclusive_group()
args = parser.parse_args()

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
context = Context(tmpDir)
if not os.path.isdir(args.grassDbase) or not os.access(args.grassDbase, os.R_OK):
    sys.exit("Unable to read GRASS DBase directory")
grassDbase = os.path.abspath(args.grassDbase)
grassConfig = GRASSConfig(context, grassDbase, args.grassLocation, args.grassMapset)
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
        sys.exit("Failed to zoom in to map %s while rendering image %s" % \
                 (RECLASS_MAP_TMP, imageFilename) )
        
# Set environment variables for GRASS PNG output driver
os.environ['GRASS_RENDER_IMMEDIATE'] = 'FALSE'
os.environ['GRASS_TRUECOLOR'] = 'TRUE'
os.environ['GRASS_WIDTH'] = '960'
os.environ['GRASS_HEIGHT'] = '720'

# 3. Open file ending in "patch.daily" in rhessys output dir
print("Reading RHESSys output data (this may take a while)...")
f = open(patchDailyFilepath)
data = RHESSysCalibratorPostprocess.readColumnsFromPatchDailyFile(f, variables)
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
        sys.exit("Failed to create reclass map for date %s" % (str(date),) )
        
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
                                         at='15,90,82,87')
    if result != 0:
        sys.exit("Failed to add legend to map while rendering image %s" % \
                 (imageFilename,) )
    
    # Set high
    if args.rescale:
        result = grassLib.script.run_command('d.text',
                                             text='High',
                                             size=5,
                                             color='black',
                                             at='90,20',
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
                                             at='89,88',
                                             align='cc')
        if result != 0:
            sys.exit("Failed to add low scale legend to map while rendering image %s" % \
                     (imageFilename,) )
    
    # Set title
    result = grassLib.script.run_command('d.text',
                                         text=title,
                                         size=5,
                                         color='black',
                                         at='75,98',
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
# e.g. ffmpeg -r 1/5 -i img%03d.png -c:v libx264 -r 30 -pix_fmt yuv420p out.mp4
cmd = "%s -y -r %d -i %s%%04d.png -c:v libx264 -pix_fmt yuv420p %s" % (FFMPEG_PATH, args.fps, RECLASS_MAP_TMP, outputFilePath)
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
