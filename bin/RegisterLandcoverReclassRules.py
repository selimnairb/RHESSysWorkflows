#!/usr/bin/env python
"""@package RegisterLandcoverReclassRules

@brief Generate landcover raster maps reclassification rules for use with GenerateLandcoverMaps.py.

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


Pre conditions
--------------
1. Configuration file must define the following sections and values:
   'SCRIPT', 'ETC'
   
2. The following metadata entry(ies) must be present in the study area section of the metadata associated with the project directory:
   landcover_type [required only if --generateKnownRules is supplied]
   
3. The following metadata entry(ies) must be present in the RHESSys section of the metadata associated with the project directory:
   rhessys_dir

Post conditions
---------------
1. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   landcover_road_rule
   landcover_impervious_rule
   landcover_landuse_rule
   landcover_stratum_rule
   landcover_lai_rule [if LAI flag is specified]

Usage:
@code
RegisterLandcoverReclassRules.py -p /path/to/project_dir
@endcode

@note EcoHydroWorkflowLib configuration file must be specified by environmental variable 'ECOHYDROWORKFLOW_CFG',
or -i option must be specified.
"""
import os, sys, errno, shutil
import argparse
import textwrap

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

# Handle command line options
parser = argparse.ArgumentParser(description='Generate landcover maps in GRASS GIS')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file. Must define section "GRASS" and option "GISBASE"')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-k', '--generateKnownRules', dest='generateKnownRules', required=False, action='store_true',
                    help="Generate rules for known landcover type; known types include: %s" % (str(RHESSysMetadata.KNOWN_LC_TYPES), ) )
group.add_argument('-b', '--buildPrototypeRules', dest='buildPrototypeRules', required=False, action='store_true',
                    help='Write prototype landcover reclass rules to the project directory. You must edit these rules to match the classes in your own landcover data')
group.add_argument('-r', '--ruleDir', dest='ruleDir', required=False,
                    help="The directory where landcover reclass rules can be found; should contain these files %s" % (str(RHESSysMetadata.LC_RULES),) )
parser.add_argument('-l', '--includeLaiRules', dest='includeLaiRules', required=False, action='store_true',
                    help='Make LAI map')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile) 

# Check for necessary information in metadata
metadata = RHESSysMetadata.readRHESSysEntries(context)
studyArea = RHESSysMetadata.readStudyAreaEntries(context)
manifest = RHESSysMetadata.readManifestEntries(context)

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])

# Get path of place to store reclass rules
projectDirRuleDir = paths.getReclassRulesDirectory()

# Write prototype landcover reclass rules to the project directory
if args.buildPrototypeRules:
    sys.stdout.write('Generating prototype landcover reclass rules...')
    sys.stdout.flush()
    # Road rule
    roadRulePath = os.path.join(projectDirRuleDir, RHESSysMetadata.LC_RULE_ROAD)
    with open(roadRulePath, 'w') as f:
        f.write('22 23 24 31 = 1 road\n')
        f.write('* = NULL\n')
    # Impervious rule
    imperviousRulePath = os.path.join(projectDirRuleDir, RHESSysMetadata.LC_RULE_IMPERVIOUS)
    with open(imperviousRulePath, 'w') as f:
        f.write('22 23 24 31 = 1 impervious\n')
        f.write('* = 0 pervious\n')
    # Landuse rule
    landuseRulePath = os.path.join(projectDirRuleDir, RHESSysMetadata.LC_RULE_LANDUSE)
    with open(landuseRulePath, 'w') as f:
        f.write('11 12 31 41 42 43 51 52 71 thru 74 90 95 = 1 undeveloped\n')
        f.write('81 82 = 2 agriculture\n')
        f.write('21 22 23 24 = 3 urban\n')
    # Stratum rule
    stratumRulePath = os.path.join(projectDirRuleDir, RHESSysMetadata.LC_RULE_STRATUM)
    with open(stratumRulePath, 'w') as f:
        f.write('11 12 21 22 23 24 31 73 74 82 = 1 nonveg\n')
        f.write('71 72 81 95 = 2 grass\n')
        f.write('41 43 90 = 3 deciduous\n')
        f.write('42 51 52 = 4 evergreen\n')
    if args.includeLaiRules:
        # LAI rule
        laiRulePath = os.path.join(projectDirRuleDir, RHESSysMetadata.LC_RULE_LAI)
        with open(laiRulePath, 'w') as f:
            f.write('11:12:0.0\n')
            f.write('21:24:0.0\n') 
            f.write('31:31:0.0\n') 
            f.write('73:74:0.0\n') 
            f.write('82:82:0.0\n')
            f.write('71:72:1.5\n')
            f.write('81:81:1.5\n')
            f.write('95:95:1.5\n')
            f.write('41:41:5.0\n')
            f.write('43:43:5.0\n')
            f.write('90:90:5.0\n')
            f.write('42:42:6.0\n')
            f.write('51:52:6.0\n')
            
    ruleDir = None
    sys.stdout.write('done\n')

# Generate rules for known landcover type
if args.generateKnownRules:
    # Check for necessary information in metadata
    if not 'landcover_type' in studyArea:
        sys.exit("Metadata in project directory %s does not contain a landcover type" % (context.projectDir,) )
    
    landcoverType = studyArea['landcover_type']
    if landcoverType not in RHESSysMetadata.KNOWN_LC_TYPES:
        sys.exit("Landcover type '%s' is not known, so rules cannot be generated." % (landcoverType,) )
    scriptEtc = context.config.get('SCRIPT', 'ETC')
    ruleDir = os.path.join(scriptEtc, landcoverType)

# Import rules from elsewhere
if args.ruleDir:
    if not os.access(args.ruleDir, os.R_OK):
        sys.exit("Unable to read rule directory %s" % (ruleDir,) )
    ruleDir = os.path.abspath(args.ruleDir)

if ruleDir:
    sys.stdout.write(textwrap.fill("Importing landcover reclass rules from %s ..." % (ruleDir,) ) )
    sys.stdout.flush()
    # Copy rules into project directory
    roadRulePath = os.path.join(ruleDir, RHESSysMetadata.LC_RULE_ROAD)
    shutil.copy(roadRulePath, projectDirRuleDir)
    imperviousRulePath = os.path.join(ruleDir, RHESSysMetadata.LC_RULE_IMPERVIOUS)
    shutil.copy(imperviousRulePath, projectDirRuleDir)
    landuseRulePath = os.path.join(ruleDir, RHESSysMetadata.LC_RULE_LANDUSE)
    shutil.copy(landuseRulePath, projectDirRuleDir)
    stratumRulePath = os.path.join(ruleDir, RHESSysMetadata.LC_RULE_STRATUM)
    shutil.copy(stratumRulePath, projectDirRuleDir)
    if args.includeLaiRules:
        laiRulePath = os.path.join(ruleDir, RHESSysMetadata.LC_RULE_LAI)
        shutil.copy(laiRulePath, projectDirRuleDir)
    sys.stdout.write('done\n')
    
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'landcover_stratum_rule', os.path.join(RHESSysMetadata.RULES_DIR, os.path.basename(stratumRulePath)) )
RHESSysMetadata.writeRHESSysEntry(context, 'landcover_landuse_rule', os.path.join(RHESSysMetadata.RULES_DIR, os.path.basename(landuseRulePath)) )
RHESSysMetadata.writeRHESSysEntry(context, 'landcover_impervious_rule', os.path.join(RHESSysMetadata.RULES_DIR, os.path.basename(imperviousRulePath)) )
RHESSysMetadata.writeRHESSysEntry(context, 'landcover_road_rule', os.path.join(RHESSysMetadata.RULES_DIR, os.path.basename(roadRulePath)) )
if args.includeLaiRules:
    RHESSysMetadata.writeRHESSysEntry(context, 'landcover_lai_rule', os.path.join(RHESSysMetadata.RULES_DIR, os.path.basename(laiRulePath)) )

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)