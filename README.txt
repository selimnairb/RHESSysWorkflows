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
		

Installation
------------

1. Install non-Python dependencies

  - OS X 10.6 through 10.8:

	1. Xcode (OS X developer tools):
		OS X 10.6: 
		OS X 10.7 and 10.8:
			- Install Xcode from the App Store
			- Launch Xcode
			- Install 'Command Line Tools':
				- Xcode > Preferences… > Downloads
	
	2. Python 2.7:
		If you are running OS X 10.6, you must first install Python 2.7, which can be downloaded from:
	3. 

  - Linux: 


2. Install PIP, a tool for installing Python modules

sudo easy_install pip


3. Install RHESSysWorkflows (including EcohydroLib) Python modules

[Linux: 'sudo pip install GDAL' first]

sudo pip install rhessysworkflows


4. Setup NLCD2006 data [optional]

  If you want to use NLCD2006 land cover data, do the following:

  - Download NLCD2006 data from:

  - Copy NLCD2006 archive to the parent folder where you would like to store it
    - For example, under OS X, create a folder called 'data' in your home directory

  - Unpack NLCD2006 data
    - For example, under OS X, DO NOT double-click on the NLCD2006 archive, but instead
      unzip the data from Terminal:
      	unzip NLCD2005_landcover_4-20-11.se5.zip


5. Setup pre-packaged NHDPlusV2 data [optional]

If you want to determine your study area based on an NHD catchment drained by a USGS streamflow gage, do the following:

  - Download pre-packaged NHDPlusV2 data from:
  
  	Note, this may take a while to download

  - Copy the pre-packaged NHDPlusV2 archive to the parent folder where you would like to store it
    - For example, under OS X, create a folder called 'data' in your home directory

  - Unpack NHDPlusV2 data (e.g. into your "Documents" folder)
    - For example, under OS X, double-click on the NHDPlusV2 archive. Note, this may take a while to unpack


6. Setup EcohydroLib and RHESSys workflows configuration file

  - Copy and paste example configuration into a text file named '.ecohydro.cfg', save this file in your home directory.

  - Modify example configuration to point to your NHDPlusV2 and NLCD2006 data:
    - If you are using OS X, and if you placed the data in a directory called 'data' in your
      home directory, the only changes you need to make is to substitute '<myusername>' with your user name.
        - To find out your OS X user name, enter the following in your Terminal:
          whoami
         
  - Set ECOHYDROLIB_CFG environment variable:
    - For example, under OS X, from your terminal, do the following:
	- Open your bash profile in an editor:
		nano ~/.bash_profile
	- Add the following at the end of the file:
		export ECOHYDROLIB_CFG=${HOME}/.ecohydro.cfg
	- Save the file
	- Re-load your bash profile (or close and open a new Terminal window):
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
