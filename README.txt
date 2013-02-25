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
[RHESSys](http://fiesta.bren.ucsb.edu/~rhessys/) data preparation workflows.  These scripts 
build on the workflow system defined by
[EcohydrologyWorkflowLib](https://github.com/selimnairb/EcohydrologyWorkflowLibWorkflow).


Installation
------------
Using Python PyPi:

easy_install --script-dir /path/to/install/scripts rhessysworkflows

It is recommended that you install the workflow scripts in a location distinct from
where your Python packages are installed (usually 'site-packages').  This is accomplished by 
specifying the --script-dir option to easy install (see above).  


Required runtime software
-------------------------
- GRASS GIS (http://grass.osgeo.org)



Configuration files
-------------------
Many scripts in both RHESSysWorkflows and EcohydrologyWorkflowLib require a configuration 
file to specify locations to executables and datasets required by the ecohydrology 
workflow libraries.  The configuration file can be specified via the environmental variable
ECOHYDROWORKFLOW_CFG or via command line option. Here is an example configuration file:

		[GDAL/OGR]
		PATH_OF_OGR2OGR = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/ogr2ogr
		PATH_OF_GDAL_RASTERIZE = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdal_rasterize
		PATH_OF_GDAL_WARP = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdalwarp
		PATH_OF_GDAL_TRANSLATE = /Library/Frameworks/GDAL.framework/Versions/Current/Programs/gdal_translate
		
		[NHDPLUS2]
		PATH_OF_NHDPLUS2_DB = /Users/<user>/Research/data/GIS/NHDPlusV21/national/NHDPlusDB.sqlite
		PATH_OF_NHDPLUS2_CATCHMENT = /Users/<user>/Research/data/GIS/NHDPlusV21/national/Catchment.sqlite
		PATH_OF_NHDPLUS2_GAGELOC = /Users/<user>/Research/data/GIS/NHDPlusV21/national/GageLoc.sqlite
		
		[SOLIM]
		PATH_OF_SOLIM = /Users/<user>/solim/solim.out
		
		[NLCD]
		PATH_OF_NLCD2006 = /Users/<user>/NLCD2006/nlcd2006/nlcd2006_landcover_4-20-11_se5.img
		
		[HYDRO1k]
		PATH_OF_HYDRO1K_DEM = /Users/<user>/HYDRO1k/na/na_dem.bil
		
		[UTIL]
		PATH_OF_FIND = /usr/bin/find
		PATH_OF_SEVEN_ZIP = /opt/local/bin/7z
		PATH_OF_SQLITE = /opt/local/bin/sqlite3
		
		[SCRIPT]
		ETC =/path/to/install/scripts/RHESSysWorkflows/etc
		
		[GRASS]
		GISBASE = /Applications/GRASS-6.4.app/Contents/MacOS
		MODULE_PATH = /Library/GRASS/6.4/Modules/bin
		MODULE_ETC = /Library/GRASS/6.4/Modules/etc
		
The 'ETC' entry in the 'SCRIPT' group should point to the 'etc' folder installed alongside the RHESSysWorkflows 
scripts. 


How to use - Typical workflow
-------------------------------
A typical workflow will consist of running data processing/registration scripts from EcohydrologyWorkflowLib. 
Once the required datasets are in place (e.g. DEM, soils, landcover, etc.) the following RHESSysWorkflows
scripts should be run (in the order listed):
1. CreateGRASSLocationFromDEM.py
2. DelineateWatershed.py
3. GenerateLandcoverMaps.py
4. GenerateSoilTextureMap.py


