#!/usr/bin/env python
"""@package ImportRHESSysSource

@brief Import RHESSys source code into project directory; Will import either from the
Git repository hosted on GitHub, from a local copy of the source tree.  The local 
source tree must be root of the RHESSys source tree and contain the following source
sub-directories: cf, g2w, and rhessys.  Will also import RHESSys ParamDB from GitHub.

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
   'GRASS', 'GISBASE'
   'RHESSYS', 'PATH_OF_GIT'
   'RHESSYS', 'PATH_OF_MAKE'

2. The following metadata entry(ies) must be present in the RHESSys section of the 
   metadata associated with the project directory: 
   rhessys_dir
   
Post conditions
---------------
1. Will import/copy source code into src directory of rhessys_dir

2. Will compile g2w (including rat), cf, and rhessys binaries into bin directory of 
   rhessys_dir 

3. Will write the following entry(ies) to the RHESSys section of metadata associated with the project directory:
   rhessys_src
   rhessys_branch or rhessys_tag (if specified)
   rhessys_sha (if ImportRHESSysSource fetched source from Git repository)
   paramdb_src
   paramdb_sha
   paramdb_dir
   paramdb
   template_template
   exec_dir (directory within project directory containing executables)
   rhessys_bin
   cf_bin
   rat_bin
   g2w_bin
   lairead_bin
   allometric_table

Usage:
@code
ImportRHESSysSource.py -p /path/to/project_dir
@endcode
"""
import os, sys, errno, stat
import argparse
import re
import shutil
from subprocess import *
from cStringIO import StringIO

from rhessysworkflows.context import Context
from rhessysworkflows.metadata import RHESSysMetadata
from rhessysworkflows.rhessys import RHESSysPaths

PARAM_DB_REPO_URL = 'https://github.com/RHESSys/ParamDB.git'
paramDBDir = 'ParamDB'
paramDBName = 'params.sqlite'
TEMPLATE_PATH = os.path.join('templates', 'template.template')
ALLOMETRIC_PATH = os.path.join('allometry', 'allometric.txt')

RHESSYS_REPO_URL = 'https://github.com/RHESSys/RHESSys.git'

# Handle command line options
parser = argparse.ArgumentParser(description='Import RHESSys source code into project directory')
parser.add_argument('-i', '--configfile', dest='configfile', required=False,
                    help='The configuration file.')
parser.add_argument('-p', '--projectDir', dest='projectDir', required=True,
                    help='The directory to which metadata, intermediate, and final files should be saved')
parser.add_argument('-s', '--sourceDir', dest='sourceDir', required=False,
                    help='The directory from which RHESys source should be copied. NOTE: will delete any sources already in the project directory')
group = parser.add_mutually_exclusive_group()
group.add_argument('-t', '--tag', dest='tag', required=False, 
                   help='Use source code from the specified tagged version of RHESSys; applies only when code is cloned from Git repository (i.e. -s not specified)')
group.add_argument('-b', '--branch', dest='branch', required=False,
                   help='Use source code from the specified branch of the RHESSys source; applies only when code is cloned from Git repository (i.e. -s not specified)')
group.add_argument('-c', '--commit', dest='commit', required=False,
                   help='Use source code from the specified commit of the RHESSys source; applies only when code is clone from Git repository (i.e. -s not specified)')
parser.add_argument('--overwrite', dest='overwrite', action='store_true', required=False,
                    help='Overwrite existing source code in the project directory; If specified, will delete existing code before importing new code.  If not specified, new code will be added to existing code.')
args = parser.parse_args()
cmdline = RHESSysMetadata.getCommandLine()

configFile = None
if args.configfile:
    configFile = args.configfile

context = Context(args.projectDir, configFile)

gisBase = context.config.get('GRASS', 'GISBASE')
gitPath = context.config.get('RHESSYS', 'PATH_OF_GIT')
makePath = context.config.get('RHESSYS', 'PATH_OF_MAKE')

# Check for necessary information in metadata
metadata = RHESSysMetadata.readRHESSysEntries(context)
if not 'rhessys_dir' in metadata:
    sys.exit("Metadata in project directory %s does not contain a RHESSys directory" % (context.projectDir,))

paths = RHESSysPaths(args.projectDir, metadata['rhessys_dir'])

paramDBPath = os.path.join(paths.DB_DIR, paramDBDir)
    
if args.overwrite:
    sys.stdout.write("Deleting existing paramDB in %s\n" % (paramDBPath,) )
    # Delete any existing source
    try:
        contents = os.listdir(paramDBPath)
        for entry in contents:
            toDelete = os.path.join(paramDBPath, entry)
            if os.path.isdir(toDelete):
                shutil.rmtree(toDelete)
            else:
                os.unlink(toDelete)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise e
        
    sys.stdout.write("Deleting existing source code in %s\n" % (paths.RHESSYS_SRC,) )
    # Delete any existing source
    try:
        contents = os.listdir(paths.RHESSYS_SRC)
        for entry in contents:
            toDelete = os.path.join(paths.RHESSYS_SRC, entry)
            if os.path.isdir(toDelete):
                shutil.rmtree(toDelete)
            else:
                os.unlink(toDelete)
    except OSError as e:
        if e.errno != errno.ENOENT:
            raise e

## 1. Fetch ParamDB
gitCommand = "%s clone %s %s" % (gitPath, PARAM_DB_REPO_URL, paramDBPath)
sha1Identifier = 'HEAD'
returnCode = os.system(gitCommand)
if returnCode != 0:
    sys.exit("Git command '%s' failed." % (gitCommand, ) )
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'paramdb_src', PARAM_DB_REPO_URL)
# Get SHA1 hash for version of ParamDB we are using, then store the hash in metadata
gitCommand = "%s rev-parse %s" % (gitPath, sha1Identifier)
process = Popen(gitCommand, shell=True, stdout=PIPE, cwd=paramDBPath)
(processStdout, processStderr) = process.communicate()
try:
    sha = processStdout.splitlines()[0]
    RHESSysMetadata.writeRHESSysEntry(context, 'paramdb_sha', sha)
except IndexError:
    pass
# Find ParamDB
contents = os.listdir(paramDBPath)
found = False
for entry in contents:
    if entry == paramDBName:
        found = True
        break
if not found:
    sys.exit("Unable to find parameter database %s in %s" % (paramDBName, paramDBPath) )
paramDB = os.path.join(paramDBPath, paramDBName)

# Make sure there is a template in the imported source
templatePath = os.path.join(paramDBPath, TEMPLATE_PATH)
#print(templatePath)
if not os.path.exists(templatePath):
    sys.exit("Template template not found in ParamDB git clone")

# Make sure there is an allometric.txt in the imported source
allometricPath = os.path.join(paramDBPath, ALLOMETRIC_PATH)
#print(allometricPath)
if not os.path.exists(allometricPath):
    sys.exit("Allometric table not found in ParamDB git clone")

RHESSysMetadata.writeRHESSysEntry(context, 'paramdb_dir', paths.relpath(paramDBPath) )
RHESSysMetadata.writeRHESSysEntry(context, 'paramdb', paths.relpath(paramDB) )
RHESSysMetadata.writeRHESSysEntry(context, 'template_template', paths.relpath(templatePath) )
RHESSysMetadata.writeRHESSysEntry(context, 'allometric_table', paths.relpath(allometricPath) )

## 2. Import code from local disk, or from GitHub            
if args.sourceDir:
    # Import source code from sourceDir
    if not os.access(args.sourceDir, os.R_OK):
        sys.exit("The specified path of the RHESSys source directory, %s, is not readable" % (args.sourceDir,) )
    if not os.path.isdir(args.sourceDir):
        sys.exit("The specified path of the RHESSys source directory, %s, is not a directory" % (args.sourceDir,) )
    
    g2wSrc = os.path.join(args.sourceDir, 'g2w')
    if not os.path.exists(g2wSrc) or not os.path.isdir(g2wSrc):
        sys.exit("The specified path of the RHESSys source directory, %s, does not seem to contain grass2world source code in a directory called 'g2w'" %
                 (args.sourceDir,) )
    
    cfSrc = os.path.join(args.sourceDir, 'cf')
    if not os.path.exists(cfSrc) or not os.path.isdir(cfSrc):
        sys.exit("The specified path of the RHESSys source directory, %s, does not seem to contain createflowpaths source code in a directory called 'cf'" %
                 (args.sourceDir,) )
    
    modelSrc = os.path.join(args.sourceDir, 'rhessys')
    if not os.path.exists(modelSrc) or not os.path.isdir(modelSrc):
        sys.exit("The specified path of the RHESSys source directory, %s, does not seem to contain RHESSys model source code in a directory called 'rhessys'" %
                 (args.sourceDir,) )
    
    # Delete paths.RHESSYS_SRC so that we can use shutil.copytree (which will recreate paths.RHESSYS_SRC)
    sys.stdout.write("Copying RHESSys source from %s..." % (args.sourceDir,) )
    sys.stdout.flush()
    shutil.rmtree(paths.RHESSYS_SRC)
    shutil.copytree(args.sourceDir, paths.RHESSYS_SRC)
    sys.stdout.write('done\n')
    # Write metadata
    RHESSysMetadata.writeRHESSysEntry(context, 'rhessys_src', os.path.abspath(args.sourceDir) )
    # Remove information about RHESSys if previously fetched from the Git repository 
    RHESSysMetadata.deleteRHESSysEntry(context, 'rhessys_branch')
    RHESSysMetadata.deleteRHESSysEntry(context, 'rhessys_tag')
    RHESSysMetadata.deleteRHESSysEntry(context, 'rhessys_sha')
    
else:   
    # Import from GitHub
    gitCommand = "%s clone %s %s" % (gitPath, RHESSYS_REPO_URL, paths.RHESSYS_SRC)
    sha1Identifier = 'HEAD'
    returnCode = os.system(gitCommand)
    if returnCode != 0:
        sys.exit("Git command '%s' failed." % (gitCommand, ) )
    # Write metadata
    RHESSysMetadata.writeRHESSysEntry(context, 'rhessys_src', RHESSYS_REPO_URL)
    
    if not args.branch and not args.tag and not args.commit:
        args.tag = 'RHESSys-5.18.2' # Default to latest stable version
    
    if args.branch or args.tag or args.commit:
        gitCommand = None
        gitSHA1Command = None
        # Check out desired branch or tag
        if args.branch:
            branchRegex = re.compile('^\s*origin/(.+)$')
            # Lookup available branches
            branches = []
            gitCommand = "%s branch -r" % (gitPath,)
            process = Popen(gitCommand, shell=True, stdout=PIPE, cwd=paths.RHESSYS_SRC)
            (processStdout, processStderr) = process.communicate()
            for line in StringIO(processStdout).readlines():
                m = branchRegex.match(line)
                if m: branches.append(m.group(1))
            
            if not args.branch in branches:
                sys.stdout.write("Branch %s not found, using default branch\n" % (args.branch,) )
            else:
                gitCommand = "%s checkout %s" % (gitPath, args.branch)
                sha1Identifier = args.branch
            # Write metadata
            RHESSysMetadata.writeRHESSysEntry(context, 'rhessys_branch', args.branch)
        if args.tag:
            # Lookup available branches
            tags = []
            gitCommand = "%s tag -l" % (gitPath,)
            process = Popen(gitCommand, shell=True, stdout=PIPE, cwd=paths.RHESSYS_SRC)
            (processStdout, processStderr) = process.communicate()
            for line in StringIO(processStdout).readlines():
                tags.append(line.strip())
            
            if not args.tag in tags:
                sys.stdout.write("Tag %s not found, using default tag\n" % (args.tag,) )
            else:
                gitCommand = "%s checkout %s" % (gitPath, args.tag)
                sha1Identifier = args.tag
            # Write metadata
            RHESSysMetadata.writeRHESSysEntry(context, 'rhessys_tag', args.tag)
        if args.commit:
            sys.stdout.write("Checking out commit {0}\n".format(args.commit))
            gitCommand = "%s checkout %s" % (gitPath, args.commit)
            sha1Identifier = args.commit
        if gitCommand:        
            # Check out the branch or tag
            process = Popen(gitCommand, shell=True, cwd=paths.RHESSYS_SRC)
            returnCode = process.wait()
            if returnCode != 0:
                sys.exit("Git command '%s' failed" % (gitCommand,) )
    # Get SHA1 hash for version of RHESSys we are using, then store the hash in metadata
    if sha1Identifier:
        gitCommand = "%s rev-parse %s" % (gitPath, sha1Identifier)
        process = Popen(gitCommand, shell=True, stdout=PIPE, cwd=paths.RHESSYS_SRC)
        (processStdout, processStderr) = process.communicate()
        try:
            sha = processStdout.splitlines()[0]
            RHESSysMetadata.writeRHESSysEntry(context, 'rhessys_sha', sha)
        except IndexError:
            pass
            
## 3. Compile code
# Set GISBASE (needed to compile g2w, cf, lairead)
os.environ['GISBASE'] = gisBase
permissions = stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR
# Build g2w
buildPath = os.path.join(paths.RHESSYS_SRC, 'g2w')
makeCommand = makePath
process = Popen(makeCommand, shell=True, cwd=buildPath)
returnCode = process.wait()
if returnCode != 0:
    sys.exit("Failed to build g2w, return code: %s" % (returnCode,) )
# Copy binaries to paths.RHESSYS_BIN
g2wSrc = os.path.join(buildPath, 'grass2world', 'g2w')
g2wDest = os.path.join(paths.RHESSYS_BIN, 'g2w')
shutil.copyfile(g2wSrc, g2wDest)
os.chmod(g2wDest, permissions)
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'g2w_bin', paths.relpath(g2wDest) )

ratSrc = os.path.join(buildPath, 'AverageTables_Unix', 'rat')
ratDest = os.path.join(paths.RHESSYS_BIN, 'rat')
shutil.copyfile(ratSrc, ratDest)
os.chmod(ratDest, permissions)
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'rat_bin', paths.relpath(ratDest) )

# Build cf
buildPath = os.path.join(paths.RHESSYS_SRC, 'cf')
makeCommand = makePath
process = Popen(makeCommand, shell=True, cwd=buildPath)
returnCode = process.wait()
if returnCode != 0:
    sys.exit("Failed to build cf, return code: %s" % (returnCode,) )

# Find the cf binary
cfBinRegex = re.compile('^cf.+$')
contents = os.listdir(buildPath)
cfBin = None
for entry in contents:
    m = cfBinRegex.match(entry)
    if m:
        cfBin = entry
        break
assert(cfBin)

# Copy binary to paths.RHESSYS_BIN
cfSrc = os.path.join(buildPath, cfBin)
cfDest = os.path.join(paths.RHESSYS_BIN, cfBin)
shutil.copyfile(cfSrc, cfDest)
os.chmod(cfDest, permissions)
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'cf_bin', paths.relpath(cfDest) )

# Build lairead
buildPath = os.path.join(paths.RHESSYS_SRC, 'util', 'GRASS', 'lairead')
makeCommand = makePath
process = Popen(makeCommand, shell=True, cwd=buildPath)
returnCode = process.wait()
if returnCode != 0:
    sys.exit("Failed to build lairead, return code: %s" % (returnCode,) )
# Copy binary to paths.RHESSYS_BIN
src = os.path.join(buildPath, 'lairead')
dest = os.path.join(paths.RHESSYS_BIN, 'lairead')
shutil.copyfile(src, dest)
os.chmod(dest, permissions)
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'lairead_bin', paths.relpath(dest) )

# Build RHESSys
buildPath = os.path.join(paths.RHESSYS_SRC, 'rhessys')
makeCommand = makePath
process = Popen(makeCommand, shell=True, cwd=buildPath)
returnCode = process.wait()
if returnCode != 0:
    sys.exit("Failed to build rhessys, return code: %s" % (returnCode,) )

# Find the RHESSys binary
rhessysBinRegex = re.compile('^rhessys.+$')
contents = os.listdir(buildPath)
rhessysBin = None
for entry in contents:
    m = rhessysBinRegex.match(entry)
    if m:
        rhessysBin = entry
        break
assert(rhessysBin)

# Copy binary to paths.RHESSYS_BIN
rhessysSrc = os.path.join(buildPath, rhessysBin)
rhessysDest = os.path.join(paths.RHESSYS_BIN, rhessysBin)
shutil.copyfile(rhessysSrc, rhessysDest)
os.chmod(rhessysDest, permissions)
# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'rhessys_bin', paths.relpath(rhessysDest) )

# Write metadata
RHESSysMetadata.writeRHESSysEntry(context, 'exec_dir', paths.relpath(paths.RHESSYS_BIN) )

sys.stdout.write('\n\nFinished importing RHESSys source\n')

# Write processing history
RHESSysMetadata.appendProcessingHistoryItem(context, cmdline)