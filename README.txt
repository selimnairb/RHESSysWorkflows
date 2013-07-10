RHESSysWorkflows			{#index}
=======================

This software is provided free of charge under the New BSD License. Please see
the following license information:

Copyright (c) 2013, University of North Carolina at Chapel Hill
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    - Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    - Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    - Neither the name of the University of North Carolina at Chapel Hill nor 
      the names of its contributors may be used to endorse or promote products
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


Authors
-------
Brian Miles <brian_miles@unc.edu>
Lawrence E. Band <lband@email.unc.edu>


Funding
-------
This work was supported by NSF grant #1239678 EAGER: Collaborative
Research: Interoperability Testbed-Assessing a Layered Architecture for
Integration of Existing Capabilities, and NSF grant #0940841 DataNet
Federation Consortium.


Introduction
------------
RHESSysWorkflows provides a series of Python scripts for performing
[RHESSys](http://fiesta.bren.ucsb.edu/~rhessys/) data preparation
workflows.  These scripts build on the workflow system defined by
[EcohydrologyWorkflowLib](https://github.com/selimnairb/EcohydrologyWorkflowLibWorkflow).


Source code
-----------
Source code can be found at https://github.com/selimnairb/RHESSysWorkflows


Configuration files
-------------------
Many scripts in both RHESSysWorkflows and EcohydroLib
require a configuration file to specify locations to executables and
datasets required by the ecohydrology workflow libraries.  The
configuration file can be specified via the environmental variable
ECOHYDROLIB_CFG or via command line option. Here is an example
configuration file:

		[GDAL/OGR]
		PATH_OF_OGR2OGR = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/ogr2ogr
		PATH_OF_GDAL_RASTERIZE = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdal_rasterize
		PATH_OF_GDAL_WARP = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdalwarp
		PATH_OF_GDAL_TRANSLATE = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdal_translate
		
		[NHDPLUS2]
		PATH_OF_NHDPLUS2_DB = /Users/<myusername>/data/NHDPlusDB.sqlite
		PATH_OF_NHDPLUS2_CATCHMENT = /Users/<myusername>/data/Catchment.sqlite
		PATH_OF_NHDPLUS2_GAGELOC = /Users/<myusername>/data/GageLoc.sqlite
		
		[NLCD]
		PATH_OF_NLCD2006 = /Users/<myusername>/data/nlcd2006_landcover_4-20-11_se5.img
		
		[UTIL]
		PATH_OF_FIND = /usr/bin/find
		#PATH_OF_SEVEN_ZIP = /opt/local/bin/7z
		PATH_OF_SQLITE = /usr/bin/sqlite3
		
		[SCRIPT]
		ETC = /System/Library/Frameworks/Python.framework/Versions/2.7/rhessysworkflows/etc
		
		[GRASS]
		GISBASE = /Applications/GRASS-6.4.app/Contents/MacOS
		MODULE_PATH = /Library/GRASS/6.4/Modules/bin
		MODULE_ETC = /Library/GRASS/6.4/Modules/etc
		
		[RHESSYS]
		PATH_OF_GIT = /usr/bin/git
		PATH_OF_MAKE = /usr/bin/make

Prototype configuration files for OS X are available here: https://github.com/selimnairb/RHESSysWorkflows/tree/master/docs/config
We'll cover how to setup your configuration file during the installation process.
		

Installation instructions
-------------------------
These instructions are tailored to OS X users, however installation under Linux is also
possible.  Linux instructions will be provided in the future.  In the mean time, Linux users
should be able to follow along to install the necessary dependencies and Python modules to
use RHESSysWorkflows; this is relatively easy to do via your distributions package manager.  
Note that if you are installing dependencies such as GDAL under Linux, you will also need to 
install the 'devel' version of these packages so that the header files necessary for compiling 
against the libraries are available.  RHESSysWorkflows may in theory work under Windows, but 
this has never been tested.  Windows users are encouraged to run a Linux distribution under a 
virtual machine.

RHESSysWorkflows is compatible with OS X 10.6, 10.7, and 10.8.  To find out what version of
OS X you are currently running, click on the apple in the upper left corner of the screen
and select *About this Mac*.  To find out the latest version of OS X you computer can run,
visit http://www.everymac.com/systems/by_capability/maximum-macos-supported.html.

Due to its age, there are a few more installation steps needed under OS X 10.6.  Also, once
Apple stops support this version of the OS, support for OS X 10.6 will also be dropped from
subsequent releases of RHESSysWorkflows.  If you were thinking of upgrading from OS X 10.6
to 10.7 or 10.8 for other reasons, this may add another.

### OS X 10.6 only: Install Python 2.7

#### Download and install Python 2.7 (for Mac OS 10.6 and later) from: http://www.python.org/download/

#### Download setuptools from: https://pypi.python.org/pypi/setuptools/0.8
Install setuptools as follows:
1. Unpack the archive by double-clicking on it in Finder
2. From Terminal:
    cd setuptools-0.8
    sudo python ez_setup.py

### Install non-Python dependencies

#### OS X 10.6: Install Xcode (OS X developer tools)
1. Download and install Xcode 3.2.6 and iOS SDK 4.3 for Snow Leopard from https://developer.apple.com/downloads/index.action (This requires you to register for a free developer account)
2. Download and install Git from http://git-scm.com/download/mac

RHESSysWorkflows uses Git to download RHESSys source code so you don't have to.

#### OS X 10.7 and 10.8: Install Xcode (OS X developer tools):
1. Install Xcode via the App Store
2. Launch Xcode
3. Install 'Command Line Tools' from menu Xcode > Preferences... > Downloads

#### Install GIS tools: GRASS QGIS
Note, GRASS version 6.4.2 is required for RHESSysWorkflows.  GRASS is used internally to
carry out workflow steps (leading to the creation of RHESSys world files and flow tables).
You will also find it useful to use GRASS to visualize the results from some workflow steps.

To install GRASS on OS X, visit http://www.kyngchaos.com/software/grass

Here you will need to download and install the following:
1. GDAL Complete 1.9 framework
2. FreeType framework
3. cairo framework
4. GRASS.app

While you are there, I recommend you also install QGIS (Quantum GIS) from http://www.kyngchaos.com/software/qgis

In addition to GRASS and components installed above, install:
1. GSL framework
2. QGIS

QGIS is useful for visualizing output for earlier workflow steps that precede the importing data into GRASS. 

#### Install GRASS Addons for RHESSysWorkflows
Download and install GRASS addons from: http://ecohydrology.web.unc.edu/files/2013/07/GRASSAddons-RHESSysworkflows.dmg_.zip

For non-OS X users, these addons (r.soils.texture and r.findtheriver) are also available for installation from
the GRASS addons repository via g.extension.  For more information, see http://grass.osgeo.org/download/addons/.

### Install Python modules
#### Install PIP, a tool for installing Python modules
Pip is the recommended way to install Python modules (i.e. rather than using easy_install). For example, Pip
allows you to easily uninstall modules.  To install pip, enter the following in a Terminal window:
    sudo easy_install pip

#### OS X 10.6: Install GDAL Python modules
Even though we installed the GDAL complete framework above, we still need to install the GDAL Python modules for
the copy of Python 2.7 we installed above; the GDAL framework only installs the Python modules for Python 2.6,
which RHESSysWorkflows is not compatible with. These installation steps are a little ugly, but bear with me 
(or upgrade from OS X 10.6). From a Terminal window type the following:
    export PATH=${PATH}:/Library/Frameworks/GDAL.framework/unix/bin
    sudo pip install --no-install GDAL
    cd /tmp/pip-build-root/GDAL
    sudo python setup.py build_ext --include-dirs=/Library/Frameworks/GDAL.framework/Headers --library-dirs=/Library/Frameworks/GDAL.framework/Versions/Current/unix/lib
    sudo pip install --no-download GDAL

#### Install RHESSysWorkflows Python modules (including EcohydroLib) 
To install RHESSysWorkflows and its dependencies (including EcohydroLib), enter the following from your Terminal:
    sudo pip install rhessysworkflows

This may take a while as several of the modules rely on non-Python code that has to be compiled.
    
> Why are GDAL Python libraries not included as a dependency of RHESSysWorkflows? This is to make
life easier for users of OS X 10.7 and 10.8.  For these OSes, the GDAL complete installer that accompanies GRASS 
will install GDAL Python modules in the copy of Python 2.7 that ships with the OS, and the GDAL Python module does
not successfully build by itself under OS X, which would make the rhessysworkflows install fail.  
Linux users will have to make sure they install GDAL Python modules in addition to GDAL itself (e.g. via a companion package, or by 'sudo pip install GDAL').

### Install local data
RHESSysWorkflows allows you to use the National Hydrography Dataset Plus (NHD Plus) to 
locate USGS streamflow gages, or use the National Landcover Dataset (NLCD 2006). Unfortunately, 
these are large datasets and this are currently no way to query subsets of these data
over the web.  If you want to use NHDPlus or NLCD2006 in your workflows, you will have to 
download local copies of these datasets.
 
#### Setup NLCD2006 data [optional]
If you want to use NLCD2006 land cover data, do the following:
1. Download NLCD2006 data [here](https://docs.google.com/file/d/0B7aK-9pTSLS-dGVzWGRCd1NwNzQ/edit?usp=sharing)
  > It is important that you download this version of the dataset, and not the official data from 
  > http://www.mrlc.gov/nlcd06_data.php.  The offical data are packaged using a version of PkZip that
  > is not compatible with OS X's GUI or commandline unzip utilities.
2. Copy NLCD2006 archive to the parent folder where you would like to store it
  > For example, under OS X, create a folder called 'data' in your home directory
3. Unpack NLCD2006 data by double-clicking on the archive

#### Setup pre-packaged NHDPlusV2 data [optional]
If you want to determine your study area based on an NHD catchment drained by a USGS streamflow gage, 
you will need a local copy of the NHDPlusV2 data.  You can obtain these data by downloading 
all or a subset of the NHDPlusV2 data and building the database as described in the [EcohydroLib
documentation](https://github.com/selimnairb/EcohydroLib).  Alternatively, you can download a pre-built
copy of the NHDPlusV2 database needed by RHESSysWorkflows [here](https://docs.google.com/file/d/0B7aK-9pTSLS-dGVzWGRCd1NwNzQ/edit?usp=sharing).
To download and unpack the pre-built data, do the following: 
1. Download pre-packaged NHDPlusV2 database [here](https://docs.google.com/file/d/0B7aK-9pTSLS-dGVzWGRCd1NwNzQ/edit?usp=sharing)
    > Note, the compressed data are nearly 7 GB, nearly 11 GB uncompressed, the download may take a while
2. Copy the pre-packaged NHDPlusV2 database archive to the parent folder where you would like to store it
    > For example, under OS X, create a folder called 'data' in your home directory
3. Unpack NHDPlusV2 database archive
    > For example, under OS X, double-click on the NHDPlusV2 archive. Note, this may take a while to unpack

### Setup EcohydroLib and RHESSysWorkflows configuration file
1. Choose the appropriate prototype configuration file from https://github.com/selimnairb/RHESSysWorkflows/tree/master/docs/config
2. Copy and paste the prototype configuration into a text file named '.ecohydro.cfg'
3. Save '.ecohydro.cfg' in your home directory
4. Modify the example configuration to point to your NHDPlusV2 and NLCD2006 data:
    > If you are using OS X, and if you placed the data in a directory called 'data' in your
    > home directory, the only changes you need to make is to substitute '<myusername>' with your user name.
    > To find out your OS X user name, use the *whoami* command in Terminal
5. Set ECOHYDROLIB_CFG environment variable so that RHESSysWorkflows can find your configuration file
    > For example, under OS X, from Terminal, do the following:
	- Open your bash profile in an editor:
		nano ~/.bash_profile
	- Add the following at the end of the file:
		export ECOHYDROLIB_CFG=${HOME}/.ecohydro.cfg
	- Save the file
	- Re-load bash profile (or close and open a new Terminal window):
		source ~/.bash_profile

How to use - Typical workflow
-------------------------------
A typical workflow will consist of running data
processing/registration scripts from EcohydrologyWorkflowLib.  Once
the required datasets are in place (e.g. DEM, soils, landcover, etc.)
the following RHESSysWorkflows scripts should be run (in the order
listed):

1. CreateGRASSLocationFromDEM.py
2. DelineateWatershed.py
3. GenerateLandcoverMaps.py
4. GenerateSoilTextureMap.py

Import RHESSys source (requires RHESSys 5.16 or later, for now use the develop branch)
