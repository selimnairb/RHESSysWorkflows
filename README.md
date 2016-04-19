**RHESSysWorkflows**			{#index}

**Introduction**

RHESSysWorkflows provides a series of Python tools for performing
[RHESSys](http://fiesta.bren.ucsb.edu/~rhessys/) data preparation
workflows.  These tools build on the workflow system defined by
[EcohydroLib](https://github.com/selimnairb/EcohydroLib).

Before reading ahead, you might want to check out 
[this screencast](http://youtu.be/vbIqsSVROiU), which provides a 
conceptual overview RHESSysWorkflows.

<!-- START doctoc generated TOC please keep comment here to allow auto update -->
<!-- DON'T EDIT THIS SECTION, INSTEAD RE-RUN doctoc TO UPDATE -->
**Table of Contents**

- [Authors](#authors)
- [Funding](#funding)
- [Source code](#source-code)
- [Installation instructions](#installation-instructions)
  - [Installing on OS X using Homebrew](#installing-on-os-x-using-homebrew)
    - [Install dependencies for GRASS, QGIS, and RHESSysWorkflows](#install-dependencies-for-grass-qgis-and-rhessysworkflows)
    - [Install RHESSysWorkflows and Python packages](#install-rhessysworkflows-and-python-packages)
      - [Upgrading to a new version of RHESSysWorkflows](#upgrading-to-a-new-version-of-rhessysworkflows)
    - [Install GRASS and QGIS](#install-grass-and-qgis)
  - [Installing on Ubuntu Linux 14.04 or 15.04](#installing-on-ubuntu-linux-1404-or-1504)
    - [Install RHESSysWorkflows and Python packages under Linux](#install-rhessysworkflows-and-python-packages-under-linux)
      - [Upgrading to a new version of RHESSysWorkflows](#upgrading-to-a-new-version-of-rhessysworkflows-1)
  - [A note on RHESSysWorkflows version numbers](#a-note-on-rhessysworkflows-version-numbers)
    - [Install GRASS Addons for RHESSysWorkflows](#install-grass-addons-for-rhessysworkflows)
  - [Setup EcohydroLib and RHESSysWorkflows configuration file](#setup-ecohydrolib-and-rhessysworkflows-configuration-file)
- [Using RHESSysWorkflows - Introduction](#using-rhessysworkflows---introduction)
- [Using RHESSysWorkflows - Typical workflows](#using-rhessysworkflows---typical-workflows)
  - [National spatial data workflow](#national-spatial-data-workflow)
    - [Specify a USGS streamflow data to locate on the NHD network](#specify-a-usgs-streamflow-data-to-locate-on-the-nhd-network)
    - [Extract NHD catchments that drain through the streamflow gage](#extract-nhd-catchments-that-drain-through-the-streamflow-gage)
    - [Get bounding box for study area](#get-bounding-box-for-study-area)
    - [Acquire terrain data from U.S. Geological Survey](#acquire-terrain-data-from-us-geological-survey)
    - [Extract landcover data from local NLCD 2006 or 2011 data](#extract-landcover-data-from-local-nlcd-2006-or-2011-data)
    - [Download soils data from SSURGO](#download-soils-data-from-ssurgo)
    - [Registering custom local data: LAI data](#registering-custom-local-data-lai-data)
    - [Create a new GRASS location](#create-a-new-grass-location)
    - [Import RHESSys source code into your project](#import-rhessys-source-code-into-your-project)
    - [Import RHESSys climate data](#import-rhessys-climate-data)
    - [Create climate stations map](#create-climate-stations-map)
    - [Delineate watershed and generate derived data products](#delineate-watershed-and-generate-derived-data-products)
    - [Generating a patch map](#generating-a-patch-map)
    - [Generating soil texture map](#generating-soil-texture-map)
    - [Import LAI map into GRASS](#import-lai-map-into-grass)
    - [Generate landcover maps in GRASS](#generate-landcover-maps-in-grass)
    - [Creating the worldfile for a watershed](#creating-the-worldfile-for-a-watershed)
    - [Creating the flow table](#creating-the-flow-table)
    - [Initializing vegetation carbon stores](#initializing-vegetation-carbon-stores)
    - [Running RHESSys models](#running-rhessys-models)
  - [Working in watersheds outside the United States](#working-in-watersheds-outside-the-united-states)
  - [Custom local data workflow](#custom-local-data-workflow)
    - [Import a DEM into your project](#import-a-dem-into-your-project)
    - [Use a DEM with streams and storm drains burned into it](#use-a-dem-with-streams-and-storm-drains-burned-into-it)
    - [Import streamflow gage coordinates](#import-streamflow-gage-coordinates)
    - [Importing data into GRASS for use with RHESSys](#importing-data-into-grass-for-use-with-rhessys)
    - [Importing other raster layers](#importing-other-raster-layers)
      - [Landcover data](#landcover-data)
      - [Rooftop connectivity](#rooftop-connectivity)
      - [Vegetation LAI](#vegetation-lai)
      - [Custom patch map](#custom-patch-map)
      - [Custom soils data](#custom-soils-data)
      - [Climate station zone map](#climate-station-zone-map)
      - [Isohyet map](#isohyet-map)
    - [Generating RHESSys definitions for custom soil data](#generating-rhessys-definitions-for-custom-soil-data)
    - [Creating a world file template in areas with low slope](#creating-a-world-file-template-in-areas-with-low-slope)
    - [Creating a surface flow table using a roof connectivity map](#creating-a-surface-flow-table-using-a-roof-connectivity-map)
    - [Creating the worldfile and initializing vegetation carbon stores](#creating-the-worldfile-and-initializing-vegetation-carbon-stores)
    - [Running custom commands](#running-custom-commands)
    - [Creating multiple worldfiles based on subbasins](#creating-multiple-worldfiles-based-on-subbasins)
- [Appendix](#appendix)
  - [Visualizing RHESSys output](#visualizing-rhessys-output)
    - [OS X](#os-x)
    - [Linux (Debian/Ubuntu-based systems)](#linux-debianubuntu-based-systems)
  - [Deprecated installation instructions](#deprecated-installation-instructions)
    - [OS X 10.7 through 10.10 using Kyngchaos GIS packages](#os-x-107-through-1010-using-kyngchaos-gis-packages)
      - [Install Xcode (OS X developer tools):](#install-xcode-os-x-developer-tools)
      - [Install RHESSysWorkflows Python modules (including EcohydroLib)](#install-rhessysworkflows-python-modules-including-ecohydrolib)
      - [Install GRASS Addons for RHESSysWorkflows](#install-grass-addons-for-rhessysworkflows-1)
      - [Setup EcohydroLib and RHESSysWorkflows configuration file](#setup-ecohydrolib-and-rhessysworkflows-configuration-file-1)
    - [OS X 10.6](#os-x-106)
      - [Download and install Python 2.7 from: http://www.python.org/download/](#download-and-install-python-27-from-httpwwwpythonorgdownload)
      - [Download setuptools from: https://pypi.python.org/pypi/setuptools/0.8](#download-setuptools-from-httpspypipythonorgpypisetuptools08)
      - [Install Xcode (OS X developer tools)](#install-xcode-os-x-developer-tools)
      - [Install PIP, a tool for installing Python modules](#install-pip-a-tool-for-installing-python-modules)
      - [Install GIS tools: GRASS & QGIS](#install-gis-tools-grass-&-qgis)
      - [Install GDAL Python modules](#install-gdal-python-modules)
      - [Install RHESSysWorkflows Python modules (including EcohydroLib)](#install-rhessysworkflows-python-modules-including-ecohydrolib-1)
      - [Install GRASS Addons for RHESSysWorkflows](#install-grass-addons-for-rhessysworkflows-2)
      - [Setup EcohydroLib and RHESSysWorkflows configuration file](#setup-ecohydrolib-and-rhessysworkflows-configuration-file-2)
  - [Install local data](#install-local-data)
    - [Setup NLCD2006 data](#setup-nlcd2006-data)
    - [Setup pre-packaged NHDPlusV2 data](#setup-pre-packaged-nhdplusv2-data)

<!-- END doctoc generated TOC please keep comment here to allow auto update -->


Authors
-------
Brian Miles - brian_miles@unc.edu

Lawrence E. Band - lband@email.unc.edu

For questions or support contact [Brian Miles](brian_miles@unc.edu)


Funding
-------
This work was supported by the following NSF grants

- Award no. 1239678 EAGER: Collaborative Research: Interoperability
   Testbed-Assessing a Layered Architecture for Integration of
   Existing Capabilities

- Award no. 0940841 DataNet Federation Consortium.

- Award no. 1148090 Collaborative Research: SI2-SSI: An Interactive Software
   Infrastructure for Sustaining Collaborative Innovation in the
   Hydrologic Sciences


Source code
-----------
Source code can be found at: https://github.com/selimnairb/RHESSysWorkflows

Documentation can be found at: http://pythonhosted.org/rhessysworkflows
		

Installation instructions
-------------------------
These instructions will lead you through installing RHESSysWorkflows
(and EcohydroLib) as well as GRASS 6.4 and QGIS open source GIS
applications; GRASS is required by RHESSysWorkflows, and QGIS is
convenient to have for visualizing GIS data acquired and produced as
you make RHESSys models.

These instructions are tailored to OS X and Linux users (specifically 
Ubuntu 14.04, or 15.04; 15.10 is not compatible as it
ships with GRASS 7 rather than GRASS 6.4), however installation
under other Linux distributions is also possible. RHESSysWorkflows may in 
theory work under Windows, but this has never been tested.  Windows users 
are encouraged to run an Ubuntu under a virtual machine.

RHESSysWorkflows is compatible with OS X 10.6 through 10.11, but only
versions 10.9 through 10.11 are officially supported.  For installation
instructions for OS X 10.6 through 10.8, see 
[Deprecated installation instructions](#deprecated-installation-instructions)
toward the end of this document.

To find out what version of OS X you are currently running, click on
the apple in the upper left corner of the screen and select *About
this Mac*.  To find out the latest version of OS X you computer can
run, visit this helpful
[page](http://www.everymac.com/systems/by_capability/maximum-macos-supported.html).

If you encounter problems during installation, please check the
[installation
notes](https://github.com/selimnairb/RHESSysWorkflows/wiki/Installation-Notes)
before contacting the developers for support.


### Installing on OS X using Homebrew
Previous [methods](#deprecated-installation-instructions) for
installing RHESSysWorkflows under OS X relied on the official GRASS
6.4 GIS
[packages](https://grass.osgeo.org/download/software/mac-osx/).
Unfortunately, the official GRASS 6.4 (and the new GRASS 7 for that
matter) are not compatible with new security enhancements in OS X
10.11 (El Capitan).  Rather than disable this new security measure
(called System Integrity Protection), we recommend that
RHESSysWorkflows users use a new [Homebrew](http://brew.sh/)-based
installation method, which will install GRASS without requiring that 
the security features of your operating system be disabled.

Homebrew is a third-party package management system that makes it easy
to install open-source software under OS X.  Each software package one
can install through Homebrew is called a formula.  To search for
available software formula, visit
[Braumeister](http://braumeister.org).

- Install Homebrew by following the instructions [here](http://brew.sh).

> During installation you may be prompted to install OS X command line
> developer tools.  Choose "Install".

**If you already have Homebrew installed, make sure to do the following
before proceeding**:
```
brew update
brew upgrade
```

- Next, install the OSGeo4Mac tap for Homebrew by following the instructions 
[here](https://github.com/OSGeo/homebrew-osgeo4mac).

> A tap allows software developers to maintain a collection of
> software formulae; OSGeo4Mac curates a number of formula related to
> open source GIS software.

Now Homebrew is installed and we just need to install a few software
dependencies before installing RHESSysWorkflows.

#### Install dependencies for GRASS, QGIS, and RHESSysWorkflows
First, install XQuartz, which is needed by GRASS, by running the
following command from the Terminal application:

    brew install Caskroom/cask/xquartz

Next, install Python 2.7:

    brew install python

> Note, this will install a separate copy of Python 2.7 so it will not
> interfere with the copy of Python 2 that ships with OS X.

#### Install RHESSysWorkflows and Python packages
To install RHESSysWorkflows and its dependencies (including EcohydroLib), 
enter the following from the terminal Terminal:

    pip install rhessysworkflows

##### Upgrading to a new version of RHESSysWorkflows
To upgrade to a newer version of RHESSysWorkflows, enter the following
into the Terminal:

    pip install rhessysworkflows --upgrade --force-reinstall
    
If pip does not install the version you expect, it may be necessary
to first remove RHESSysWorkflows and Ecohydrolib before installing the 
new version (especially under Linux where some Python packages fail to
build when installed via *pip*):

    pip uninstall rhessysworkflows
    pip uninstall ecohydrolib

Then install as above:

    pip install rhessysworkflows
    
#### Install GRASS and QGIS
Install GRASS and QGIS using Homebrew as follows from the Terminal:

    brew install grass-64 gdal-20 qgis-214 --without-server ffmpeg
    brew link grass-64 --force
    brew linkapps qgis-214
    
You will also need to install a Python library for accessing PostGIS
geospatial databases; This is required by QGIS:
    
    pip install psycopg2 # Do after installing QGIS, which will install PostqreSQL

This concludes the OS X Homebrew-specific portion of the installation
instructions.


### Installing on Ubuntu Linux 14.04 or 15.04
Install RHESSysWorkflows/EcohydroLib dependencies using apt-get:

    sudo apt-get install build-essential git subversion p7zip-full \
    python python-dev python-pip python-scipy \
    libxml2-dev libxslt-dev \
    gdal gdal-bin python-gdal \
    grass grass-dev \
    libbsd-dev ffmpeg vlc

Note: the above works for Ubuntu 14.04.  For 15.04 the packaging of 
GDAL has changed use the following to install dependencies under
Ubuntu 15.04:

    sudo apt-get install build-essential git subversion p7zip-full \
    python python-dev python-pip python-scipy \
    libxml2-dev libxslt-dev \
    libgdal-dev libgdal-doc gdal-bin python-gdal \
    grass grass-dev \
    libbsd-dev ffmpeg vlc
    
> Ubuntu 15.10 is not compatible with RHESSys or RHESSysWorkflows
> as this version of Ubuntu uses GRASS 7, which is not yet supported
> by RHESSys or RHESSysWorkflows.  If you want to use another 
> Linux distribution, make sure that it provides similar versions
> of the above dependencies.

#### Install RHESSysWorkflows and Python packages under Linux
To install RHESSysWorkflows and its dependencies (including EcohydroLib), 
enter the following from your Terminal:

    sudo pip install rhessysworkflows

##### Upgrading to a new version of RHESSysWorkflows
To upgrade to a newer version of RHESSysWorkflows, enter the following into the Terminal:

    sudo pip install rhessysworkflows --upgrade --force-reinstall
    
If pip does not install the version you expect, it may be necessary
to first remove RHESSysWorkflows and Ecohydrolib before installing the 
new version (especially under Linux where some Python packages fail to
build when installed via *pip*):

    sudo pip uninstall rhessysworkflows
    sudo pip uninstall ecohydrolib

Then install as above:

    sudo pip install rhessysworkflows

This concludes the Linux-specific portion of the installation instructions.

### A note on RHESSysWorkflows version numbers   
Each project can only be used with compatible versions of
RHESSysWorkflows/Ecohydrolib.  Compatible versions are those that
write the same version number to the metadata store for a given
project.  This compatibility check is necessary to ensure both
scientific reproducibility and to make sure your workflows do not
become corrupted by incompatible versions.  We strive to maintain
compatibility between releases of RHESSysWorkflows/Ecohydrolib,
however sometimes enabling new workflow scenarios requires
incompatible changes.  The release notes for each release will note
when a new version breaks backward compatibility.  The good news is
that you can have multiple copies of RHESSysWorkflows/Ecohydrolib
installed on your computer at the same time.  To do so, you must do
the following:

1. Install [virtualenv](https://pypi.python.org/pypi/virtualenv)

2. Create a new virtual environment for each version of
RHESSysWorkflows you would like to run

3. Activate a virtual environment you would like to install a specific
version of RHESSysWorkflows into

4. Install RHESSysWorkflows in the virtual environment, for example to
install version 1.0:

    pip install rhessysworkflows==1.0
    
Not that you do not need to use 'sudo' when running in a virtual
environment as the files are installed in a directory owned by your
user account.

#### Install GRASS Addons for RHESSysWorkflows
Follow these steps to install the GRASS addons under OS X and Linux:

1. Start GRASS:

 - OS X: In the Terminal, type:
```
brew link gettext --force   # Make sure GRASS's g.extension program can find gettext, which is used in internationalization.
grass64
```

 - Linux: on a command line type: 
 ```
 grass64
 ```
    
2. Create a new location (it doesn't matter where, we'll only use it to run
the g.extension command to install the extensions).

3. Install r.soils.texture

    g.extension extension=r.soils.texture

4. Install r.findtheriver

    g.extension extension=r.findtheriver

5. Exit GRASS (close all GUI windows, then type *exit* in the GRASS
command line window).

6. On OS X only, once you have exited GRASS do the following:
```
brew unlink gettext     # Re-hide the version of gettext installed by Homebrew, which may conflict of that of OS X.
```

For more information on these addons (r.soils.texture and r.findtheriver), see:
- [r.findtheriver](http://grasswiki.osgeo.org/wiki/AddOns/GRASS_6#r.findtheriver)
and r.soils.texture
- [r.soils.texture](http://grasswiki.osgeo.org/wiki/AddOns/GRASS_6#r.soils.texture).

### Setup EcohydroLib and RHESSysWorkflows configuration file
- Choose the appropriate prototype configuration file:

    + [OS X](https://raw.github.com/selimnairb/RHESSysWorkflows/master/docs/config/ecohydro-OSX-homebrew.cfg)
    
    + [Linux](https://raw.github.com/selimnairb/RHESSysWorkflows/master/docs/config/ecohydro-Linux.cfg)

- Save into a file named '.ecohydro.cfg' stored in your home directory
and replace all occurances of *&lt;myusername&gt;* with your user name
(To find out your OS X or Linux user name, use the *whoami* command in
Terminal).
    
- Set ECOHYDROLIB_CFG environment variable so that RHESSysWorkflows
  can find your configuration file

    + Under OS X, from Terminal, do the following:

		echo "export ECOHYDROLIB_CFG=${HOME}/.ecohydro.cfg" >> ~/.bash_profile
		
	+ If you're running Linux, do the following:
	
		echo "export ECOHYDROLIB_CFG=${HOME}/.ecohydro.cfg" >> ~/.profile
	    
	    echo "export LD_LIBRARY_PATH=/usr/lib/grass64/lib:${LD_LIBRARY_PATH}" >> ~/.profile


	+ Re-load bash profile (or close and open a new Terminal window):

		source ~/.bash_profile (~/.profile under Linux)

This concludes the configuration portion of the installation and 
configuration instructions.


Using RHESSysWorkflows - Introduction
-------------------------------------
All EcohydroLib and RHESSysWorkflows tools are executed from the
command line.  Each tool stores the data and metadata associated
with a single workflow in a directory, called a *project directory*.
Metadata are stored in a file in the project directory called
*metadata.txt*.  There can only be one metadata.txt in a project
directory, so it is essential that each workflow have its own project
directory.

In addition to automatically recording provenance information for data
and the processing steps of a workflow, the metadata store allows for
loose coupling between the tools that are used to carry out a
particular workflow. By design, each workflow tool performs roughly
one discrete function.  This allows for flexible workflows. Each
workflow tool writes a series of entries to the metadata to reflect
the work done by the tool.  Most workflow tools require certain
entries to be present in the metadata store to perform the work they
will do.  For example, before DEM data for the study are can be
downloaded from DEMExplorer, the bounding box for the study area must
be known. The tool that queries DEMExplorer need not know how the
bounding box was generated, it only cares that the bounding box is
present in the metadata store.  Lastly, the metadata store helps users
to orchestrate workflows by requiring that only new information
required at each step be entered to run a particular command, other
information required can be queried from the metadata.

Each workflow tool will print usage information when run on its own
for example running:

    GetNHDStreamflowGageIdentifiersAndLocation.py 

Will yield:

    usage: GetNHDStreamflowGageIdentifiersAndLocation.py [-h] [-i CONFIGFILE] -p
    PROJECTDIR -g GAGEID
    GetNHDStreamflowGageIdentifiersAndLocation.py: error: argument -p/--projectDir is required

This indicates that the -p (a.k.a. --projectDir) argument is required;
that is, you must specify the project directory associated with
workflow for which you are running the tool.  For many
EcohydroLib/RHESSyWorkflows tools, this is the only required command
line parameter.  

It's good practice when running a command to first execute the command
with no command line arguments.  This will show you the required and
optional parameters.  To get detailed help for a given command, run
the command with the -h (a.k.a. --help) argument, for example:

    GetNHDStreamflowGageIdentifiersAndLocation.py -h
 
Note that while this particular tool, and RHESSysWorkflows tools
in general, have long names, they are long to be descriptive so as to
be easier to use.  To avoid having to type these long names out, you
are encouraged to make use of *tab* completion in Terminal.  To use
tab completion, simply type the first few characters of a command and
then hit the 'tab' key on your keyboard; the entire command name will
be 'completed' for you on the command line.  If the entire name is not
'completed' for you, hit tab again to see that list of commands that
match what you've typed so far.  Once you type enough characters to
uniquely identify the command, hitting tab once more will complete the
command name.


Using RHESSysWorkflows - Typical workflows
------------------------------------------
A typical workflow will consist of running data
processing/registration tools from EcohydroLib.  Once the required
datasets are in place (e.g. DEM, soils, landcover, etc.)
RHESSysWorkflows tools can be run to create the world file and flow
table associated with a RHESSys model.

In the following sections two example workflows are described: (1)
using data from national spatial data infrastructure (USGS, NHD, NLCD,
SSURGO, SRTM); and (2) using custom local data.  The combinations of
tools executed in these workflows represent two of the many unique
workflows possible.

### National spatial data workflow

Start by creating a directory called 'standard'.  This will be your
project directory for this example workflow.  You can create this
directory anywhere on your computer where you have write access
(e.g. in your home directory).

#### Specify a USGS streamflow data to locate on the NHD network

First, choose the USGS streamflow gage, identified by the USGS site
number, you wish to build a RHESSys model for.  Note that while you
can select gages that drain large basins, if you are planning to use
SSRUGO soils data acquired using the RHESSysWorkflows tool
GetSSURGOFeaturesForBoundingbox the study area must be less than
10,000 sq. km.

To locate the USGS gage of interest on the NHD flow line network run
the following tool:

    GetNHDStreamflowGageIdentifiersAndLocation.py -p standard -g 01589312

This will create the metadata store for your project in a file named
metadata.txt in the project directory 'standard'.  The metadata store
will be populated with the gage ID (the site number you specified on
the command line), and the NHD reachcode and reach measure associated
with this gage.  By default, RHESSysWorkflows will use a web service
to perform this query.  (If you are using a local copy of the NHDPlusV2 
data add the *-s local* command line argument to the above command; 
Most users should ignore this.)

> Note that USGS NWIS gage identifiers can begin with '0'. You must 
> enter this leading 0 when specifying a streamflow gage.

#### Extract NHD catchments that drain through the streamflow gage

The NHD database relates stream flowlines to the catchments that drain
into them.  RHESSysWorkflows can use these catchments, stored in a
shapefile in your project directory, to determine the geographic
bounding box for your study area (see below).  This bounding box can
then beused extract spatial data for your study area from datasets
stored locally as well as those available via web services interfaces.

To extract a shapefile of the NHD catchments that drain through your
streamflow gage, run the following tool:

    GetCatchmentShapefileForNHDStreamflowGage.py -p standard

(If you are using a local copy of the NHDPlusV2 data add the *-s local* 
command line argument to the above command; Most users should ignore 
this.) 

You should now see the study area shapefile in your project directory.
You can visualize the study area, along with the streamflow gage, in
QGIS.  Note that the study area shapefile does not represent the
delineation of your watershed, but should instead be a superset of the
watershed.  We will delineate your watershed using GRASS GIS.

#### Get bounding box for study area

Now that RHESSysWorkflows has a GIS representation of your study area,
it can determine the extent or bounding box (also sometimes called the
'minimum bounding rectangle') of the study area.  Do so by running the
following tool:

    GetBoundingboxFromStudyareaShapefile.py -p standard

As with many EcohydroLib/RHESSysWorkflows commands, you won't see much
in the way of output printed to the screen; don't fear.  The commands
are writing what's needed for future workflow steps to the metadata
store associated with your project directory.  If you open the
metadata store, the file called *metadata.txt* in the project
directory *standard*, you can see the bounding box coordinates stored
in the *study_area* section; look for the attribute named
*bbox_wgs84*.

#### Acquire terrain data from U.S. Geological Survey

U.S. Geological Survey (USGS) has developed a prototype web service
for downloading terrain data based on the National Elevation Dataset
(NED).  Now that we've defined the bounding box for our study area, 
it's very easy to download DEM data from this web service, as follows:

    GetUSGSDEMForBoundingbox.py -p standard

By default, this tool will download an extract terrain data for your 
study area from the National Elevation Dataset (NED) 30-meter (1/3 
arcsecond) USA DEM.  The DEM will be stored in a UTM project (WGS84 datum)
with the appropriate UTM zone chosen for you.  You can override both the DEM 
coverage type and target spatial reference system by specifying the 
appropriate command line parameters; spatial reference systems must be
refered to by their EPSG code (see http://www.spatialreference.org/ref/epsg/ 
for more information).  Additionally, you can choose to resample the DEM
extract to another spatial resolution.  To learn how to specify these
options, issue the help command line argument as follows:

    GetUSGSDEMForBoundingbox.py -h

Note that EcohydroLib/RHESSysWorkflows uses the DEM resolution,
extent, and sptial reference the reference for all other rasters
imported into or generated by subsequent workflow tools.

Lastly, you are not required to use a DEM from the USGS web service.  See the
*Custom local data workflow* example below, as well as the *Working in 
watersheds outside the United States* section for more information.

#### Extract landcover data from local NLCD 2006 or 2011 data

EcohydroLib makes it easy to import custom NLCD 2006 or 2011 tiles for your
study area into your project from web services hosted by [U.S. Geological Survey](http://raster.nationalmap.gov/arcgis/rest/services/LandCover/USGS_EROS_LandCover_NLCD/MapServer).  For example, 
to acquire NLCD 2011 data:

    GetUSGSNLCDForDEMExtent.py -p standard

This command will download an NLCD 2011 data matching the extent, resolution, 
and spatial reference of your DEM and store the tile in your project 
directory. (If you wish to give your NLCD tile a particular name, use
the *outfile* command line option.  To instead download NLCD 2006 data, do
the following:

    GetUSGSNLCDForDEMExtent.py -p standard -t NLCD2006

#### Download soils data from SSURGO

The USDA NRCS provides the [Soil Data
Mart](http://soildatamart.nrcs.usda.gov), a sophisticated web
services-based interface for querying and downloading high-resolution
SSURGO soils data.  SSURGO data are structured as a complex database
consisting of both spatial and tabular data.  For more information on
this database format and the soil survey data exposed through the
SSRUGO database please see the [SSURGO
metadata](http://soildatamart.nrcs.usda.gov/SSURGOMetadata.aspx).

EcohydroLib provides two tools that make it easy to generate soil
hydraulic properties commonly needed for ecohydrology modeling (namely
the numeric properties Ksat, porosity, percent sand, percent silt, and
percent clay).  The first tool downloads spatial mapunit features
for your study area as well as tabular soil hydraulic property data.
These spatial and tabular data are joined, and written to your project
directory as an ESRI Shapefile.  For more information on what
attributes are queried and how non-spatial mapunit commponents are
aggregated by the code, please see the EcohydroLib source code
[here](https://github.com/selimnairb/EcohydroLib/blob/master/ecohydrolib/ssurgo/featurequery.py)
and
[here](https://github.com/selimnairb/EcohydroLib/blob/master/ecohydrolib/ssurgo/attributequery.py).

To download SSURGO features and attributes into your project, run the
following command:

    GetSSURGOFeaturesForBoundingbox.py -p standard

Note that for server performance and network bandwidth issues, Soil
Data Mart limits SSURGO spatial queries to areas of less than roughly
10,000 sq. km.  For performance reasons, EcohydroLib (and therefore
RHESSysWorkflows) limits the size of SSURGO queries to ~2,500 sq. km.
If your study area is larger than this, you must instruct 
*GetSSURGOFeaturesForBoundingbox* to tile the query into multiple
sub queries.  SSURGO query tiling is enabled using the *--tile* option:

    GetSSURGOFeaturesForBoundingbox.py -p MYPROJECT_DIRECTORY --tile
    
What this does is to split the larger query to the Soil Data Mart into many
smaller queries (possibly hundreds or thousands).  The results of these
sub-queries are then automatically assembled into a single vector feature 
layer by EcohydroLib.  To reduce download times, tiled queries are by default 
performed in parallel.  The number queries to run in parallel is determined 
automatically by the number of simultaneous threads your computer supports 
(see [here](https://docs.python.org/2/library/multiprocessing.html#multiprocessing.cpu_count)
for more information).  Use the *--nprocesses* option to change the
number of SSURGO queries to perform in parallel.  For example, to 
perform 16 queries in parallel (which should be fine on an 8-thread
machine):

    GetSSURGOFeaturesForBoundingbox.py -p MYPROJECT_DIRECTORY --tile --nprocesses 16
    
To disable parallel queries:

    GetSSURGOFeaturesForBoundingbox.py -p MYPROJECT_DIRECTORY --tile --nprocesses 1

You can visualize the downloaded SSURGO features and joined tabular
data by opening the shapfile in QGIS.  The SSURGO shapefile has a
long, though descriptive, name that includes the bounding box
coordinates for your study area.  If you are unsure what shapefile in
your project directory to open, the *soil_features* attribute of the
*manifest* section of your metadata store lists the filename.  

> While you're looking at the metadata store, scroll down to the
> *provenance* section.  While the attribute names are a bit messy,
> you can see that for each manifest entry, there EcohydroLib has
> recorded detailed provenance information.  For the SSURGO soil
> features, the Soil Data Mart web services URL is listed as the
> datasource; for the DEM data downloaded from DEM Explorer,
> EcohydroLib records the exact URL used to download your DEM.
> Lastly, if you scroll down a bit farther, you can see that the
> *history* section of the metadata store records the order of every
> EcohydroLib/RHESSysWorkflow command you've run in this workflow,
> including all of the command line parameters.

EcohydroLib also provides a second tool for dealing with SSURGO soils
data.  This tool allows you to create raster maps of SSURGO mapunit
polygons using the following numeric soil properties as raster values:
Ksat, porosity, percent clay, percent silt, and percent sand).  Use
the following command to generate all of these rasters in your project
directory:

    GenerateSoilPropertyRastersFromSSURGO.py -p standard

Later on in this example workflow, we'll use the percent sand and
percent clay rasters to generate a USDA soil texture map, which we'll
use to define RHESSys soil parameters for our study watershed.

#### Registering custom local data: LAI data 

EcohydroLib does not current provide direct access to vegetation leaf
area index data from remote sensing sources.  LAI data are needed by RHESSys
to initialize vegetation carbon and nitrogen stores.  RHESSysWorkflows
relies can use a user-supplied LAI rasters to supply these initial LAI
data to RHESSys.  For this example workflow, you can download an LAI
image
[here](https://docs.google.com/file/d/0B7aK-9pTSLS-eEJaZXctaEtkb2s/edit?usp=sharing).
Use the following command to register this user-supplied raster into
your project:

    RegisterRaster.py -p standard -t lai -r /path/to/static_lai-01589312.tif -b "Brian Miles <brian_miles@unc.edu>"

To make this command work, you'll have to change the path to the file
name passed to the *-r* argument to reflect the location on your
computer to which you downloaded the example LAI image.  

> Note that EcohydroLib/RHESSysWorkflows do not work with files or
> directories whose names contain spaces.  This will be addressed in a
> future release.

Also, the extent of the LAI image doesn't quite match that of our DEM.
By default, RegisterRaster will not import a raster that does not
match the extent of the DEM.  Use the *--force* option to force
RegisterRaster to import the raster:
    
    RegisterRaster.py -p standard -t lai -r /path/to/static_lai-01589312.tif -b "Brian Miles <brian_miles@unc.edu>" --force

When using the *force* option, it is even more important that you
check the results of the command to ensure the data registered with
the workflow are appropriate for the modeling you plan to perform.  Go
ahead and browse to your project directory, find the DEM and LAI
rasters and open them in QGIS (you will likely have to set a color map
for each, otherwise all values will render in grey).

Note the *-b* (a.k.a. *--publisher*) argument given to the above
command.  When specified, this optional parameter will be stored in
the provenance matadata store entry of the raster.

RegisterRaster is a generic EcohydroLib tool that knows how to
import several types of raster into your workflow; the *-t lai*
argument indicates that we are importing an LAI raster (see the
*Custom local data workflow* for to learn how to import other raster
types).  RegisterRaster will copy the raster being imported into your
project directory; the raster will be resampled and reprojected to
match the resolution and spatial reference of the DEM already present
in the workflow.  You can choose the resampling method to use, or turn
off resampling, though the raster will be resampled if the spatial
reference system does not match that of the DEM; see the help message
for more information.

At this point, we have enough spatial data in a generic format
(e.g. GeoTIFF) to build RHESSys-specific datasets using RHESSysWorkflows.

#### Create a new GRASS location 

RHESSys requires that all spatial data used to create a world file and
flow table for a RHESSys model be stored in a GRASS GIS mapset.  We'll
start building these data in RHESSysWorkflows by creating a new GRASS
location and mapset within our project directory, and importing our
DEM into this mapset:

    CreateGRASSLocationFromDEM.py -p standard -d "RHESSys model for Dead Run 5 watershed near Catonsville, MD"

The *-d* (a.k.a. *--description") parameter is a textual description
of this GRASS location; always wrap this parameter in quotes.  If you
choose, you can specify custome names of the following GRASS
parameters:

1. dbase, the directory within the project directory where your GRASS
location will be stored (defaults to 'GRASSData') 
2. location (defaults to 'default')
3. mapset (defaults to 'PERMANENT')

> Use the *--overwrite* option to CreateGRASSLocationfromDEM to
> overwrite the GRASS location created by a previous invocation of
> CreateGRASSLocationFromDEM.  Note that most RHESSysWorkflows
> commands provide the same option.  The ability to overwrite GRASS
> datasets accomodates the often exploratory nature of ecohydrology
> data preparation workflows.  While the data will be overwritten, the
> command history stored in the metadata store will retain a listing
> of the order in which you ran all workflow steps.  This can help you
> to retrace the steps you took to arrive at the current workflow
> state.

Go ahead and open GRASS, pointing it to the dbase named *GRASSData* in 
your project directory, and then opening the mapset *PERMANENT* in 
the location *default*.  You should be able to load the DEM raster 
into the map view.  We'll use GRASS to visualize the results of the 
next few workflow steps, so keep GRASS open in the background.

#### Import RHESSys source code into your project

To create worldfiles and flow tables RHESSysWorkflows needs a copy of
RHESSys source code.  RHESSysWorkflows also uses the new RHESSys
[ParamDB](https://github.com/RHESSys/ParamDB) database and Python
libraries to generate vegetation, soil, land use and other parameters
needed by RHESSys.  RHESSysWorkflows is only compatible with the
pre-release version of RHESSys 5.16 and later versions of the code.
At present, and for first-time users, the most reliable way to import
ParamDB and RHESSys source code into your project is to download the
code from GitHub using the ImportRHESSysSource tool.  However, this
tool is also capable of importing RHESSys source code stored on your
computer.  This allows you to import the code from a previous
RHESSysWorkflows project; ParamDB is always downloaded from GitHub,
even when RHESSys source code is imported from a local source.

To download ParamDB and the RHESSys source code and store them in your
project directory issue the following command:

    ImportRHESSysSource.py -p standard

If you want to checkout an alternate branch, use the *-b* option to 
specify the Git branch of RHESSys to use (e.g. 'develop'). By default, 
ImportRHESSysSource will use the *master* branch, which is the appropriate 
branch to use with RHESSys 5.18.
	
Once ImportRHESSysSource finishes importing RHESSys source code into
the project directory, it will compile all the tools necessary to
create world files and flow tables, while also compiling the RHESSys
binary.  Once the command finishes, open the *rhessys* directory in
your project directory.  Here you can see the familiar RHESSys
directory structure for storing model parameters, templates,
worldfiles, flow tables, temporal event files, and model output; the
RHESSys tools compiled by ImportRHESSysSource will be copied into the
*bin* directory of the *rhessys* directory.  Also note that all the
source code for RHESSys is stored in the *src* directory.

#### Import RHESSys climate data 

Because of the greater variability of climate data formats, and the
complexity of time-series workflows, we have chosen to focus
development effort on RHESSysWorkflows toward making it easier to
acquire and manipulate geospatial data required for building RHESSys
work files and flow tables.  This means that the modeler is
responsible for building the climate data necessary for building
RHESSys world files and performing model runs.  

RHESSysWorkflows provides the ImportClimateData tool to import
RHESSys climate data into your project.  To run this example workflow,
download example climate data
[here](https://docs.google.com/file/d/0B7aK-9pTSLS-Q1NQbUJzVXZKeUE/edit?usp=sharing).
Unzip the file to a location on your computer (e.g. in your home
directory), this will result in a directory named *clim* in the
location.  Issue the following command to import these data:

    ImportClimateData.py -p standard -s /path/to/clim

You will have to replace */path/to/clim* with the path of the clim
folder unpacked from the zip file downloaded above.  

For your own climate data to work with ImportClimateData the data must
be stored in their own directory, with each base station having file
name that ends in *.base*.  See the help for ImportClimateData for
more information.

#### Create climate stations map

If your study watershed has multiple climate stations that you would
like to use, you must use a climate stations map to associate each
zone in your world file with a particular climate station.  RHESSysWorkflows
provides the GenerateBaseStationMap tool to create a raster map
of your climate stations using Thiessen polygons derived from climate
station points, these points must be specified in a text file in a format
supported by GRASS's 
[v.in.acsii](http://grass.osgeo.org/grass64/manuals/v.in.ascii.html) tool. 
For this tutorial, we'll use a dummy point to associated with the *bwi* 
climate station imported above.  You can download this point
[here](https://docs.google.com/file/d/0B7aK-9pTSLS-cmVWdmNxNThRc1U/edit?usp=sharing).
Once downloaded, unzip the file to reveal the text file containing the point,
which should look like this:

    1|349093.638022|4350309.809951|bwi

In a real-world case, there would be additional lines in this file,
one for each climate station.  The first column is the base station ID
and must match the base_station_ID field of the ${STATION}.base file
associated with each climate station.  

> When we create the world file template later on in this tutorial,
> the tool that we use to do so, GenerateWorldTemplate, will make sure
> that there is a climate base station file for each unique raster value
> in your base station map; the world file template will not be generated
> if this is not the case.

The second and third columns represent the X and Y coordinates (or easting 
and northing) of the point feature we will use to represent the location 
of the climate station. The final column is the name of the climate station 
and should match ${STATION} in ${STATION}.base (i.e. if your base station 
file name is 'bwi.base', the final field should be 'bwi').

Now we're ready to use GenerateBaseStationMap to: import the climate station
points; make Thiessen polygons based on the points, and rasterize the polygons:

    GenerateBaseStationMap.py -p standard -b /path/to/dummy_stations1.txt

> The GRASS tool 
> [v.voronoi](http://grass.osgeo.org/grass64/manuals/v.voronoi.html)
> is used to generate the Thiessen polygons.  Note that some versions of
> this tool can fail if you have only two points.  Hopefully this will be
> fixed when GRASS 6.4.3 is released later in 2013.

#### Delineate watershed and generate derived data products

RHESSysWorkflows automates the process of delineating your study
watershed based on the location of the streamflow gage registered in
the workflow.  As part of this process, many datasets needed by
RHESSys will be derived from the DEM.  To delineate the watershed:

    DelineateWatershed.py -p standard -t 500 -a 1.5

Here the *-t* (a.k.a. *--threshold*) parameter specifies the minimum
size (in DEM cells) for subwatersheds generated by the GRASS command
[r.watershed](http://grass.osgeo.org/grass64/manuals/r.watershed.html).

The *-a* (a.k.a. *--areaEstimate*) parameter allows you to provide a
guess of the area (in sq. km) of the delineated watershed.
DelineateWatershed will report whether the watershed is within 20% of
the area.  You can view the delineated watershed in GRASS by displaying
the raster map named *basin*.  If the area or the shape of the
delineated watershed differs greatly from what you expect, you may
need to vary how DelineateWatershed snaps your streamflow gage onto
the stream network.  This is accomplished by either changing the *-s*
(a.k.a. *--streamThreshold*) or stream threshold parameter and/or the
*-w* (a.k.a. *--streamWindow*) parameter passed to
[r.findtheriver](https://svn.osgeo.org/grass/grass-addons/grass6/raster/r.findtheriver/description.html).

To debug watershed delineation problems, it is also helpful to view
the original streamflow gage and the snapped streamflow gage overlaid
on the upslope accumulated area map (UAA). DelineateWatershed will
create vector layers for each of the streamflow gage coordinants
(named *gage* and *gage_snapped*) as well as a UAA raster map (named
*uaa*).

> Though we do not recommend that you make changes to the metadata
> store by hand, as a last resort, you can snap the gage location by
> hand using GRASS and update the *gage_easting_raw* and
> *gage_northing_raw* attributes in the *rhessys* section of the
> metadata store.  Then re-run DelineateWatershed as before with the
> addition of the *--overwrite* option.

For a listing of the derived datasets generated by DelineateWatershed,
use the GRASS command *g.list rast* or check the DelineateWatershed
[source
code](https://github.com/selimnairb/RHESSysWorkflows/blob/master/bin/DelineateWatershed.py).

#### Generating a patch map

RHESSysWorkflows provides GeneratePatchMap, an automated tool for
creating gridded and clumped patch maps.  Gridded patch maps consist
of a regular grid of the same resolution and extent as the DEM;
clumped maps can be created using elevation or topographic wetness
index rasters.  Modelers can also use custom patch maps registered via
EcohydroLib's RegisterRaster tool and imported into GRASS using
ImportRasterMapIntoGRASS (see below for a general description of this
command).

To create a gridded patch map, enter the following into your Terminal:

    GeneratePatchMap.py -p standard -t grid

To create an elevation clumped patch map:

    GeneratePatchMap.py -p standard -t clump -c elevation

... and a topographic wetness index clumped map:

    GeneratePatchMap.py -p standard -t clump -c wetness_index

Clumped patch maps are generated by calling GRASS's r.clump command
with the appropriate source raster as import.

> By default GeneratePatchMap will set the zone map to be that of the
> patch map, but only if a custom zone map has not been registered
> with the workflow (e.g. via a combination of RegisterRaster and
> ImportRasterMapIntoGRASS; see custom data tutorial below).  If you
> wish to overwrite your custom zone map with the patch map, use the 
> *--forceZone* option to GeneratePatchMap.

#### Generating soil texture map

Since we used EcohydroLib's SSURGO tools to generate percent sand
and percent clay raster maps for our watershed, we can use the GRASS
add-on r.soils.texture to generate USDA soil texture classes, for which
RHESSys's ParamDB contains parameters.  It is also possible to use
custom soil maps, which we'll explore in the *custom local data
workflow* section below.

To generate our soil texture map in GRASS, as well as the
corresponding RHESSys soil definition files, use the
GenerateSoilTextureMap tool as follows:

    GenerateSoilTextureMap.py -p standard

This command will print information about what soil texture classes
were encountered in the soil texture map, and what RHESSys soil
default IDs these classes map onto.  You can view the resulting soil
texture map (named *soil_texture*) in GRASS.  The soil definition
files will be stored in the *defs* directory of the *rhessys* directory
stored in your project directory.

#### Import LAI map into GRASS

We'll use the general command ImportRasterMapIntoGRASS to import our
LAI map from the project directory into GRASS, where RHESSys will be
able to make use of it (you can also derive an LAI map from your landcover
map; see below):

    ImportRasterMapIntoGRASS.py -p standard -t lai -m nearest

The *-m* (a.k.a. *--method*) paramer specifies how GRASS should
resample the raster being imported.  Value resampling methods are
those supported by GRASS's
[r.resamp.interp](http://grass.osgeo.org/grass64/manuals/r.resamp.interp.html)
command, as well as *none*, which will cause ImportRasterMapIntoGRASS
to skip the resampling step.

#### Generate landcover maps in GRASS

RHESSysWorkflows uses a single landcover map to generate the following maps
used by RHESSys:

- Vegetation type (stratum)
- Land use
- Roads
- Impervious surfaces
- Leaf area index (LAI; optional)

The first step in generating these maps is to import the landcover
raster from your project directory into GRASS using
ImportRasterMapIntoGRASS:

    ImportRasterMapIntoGRASS.py -p standard -t landcover -m nearest

In our case, the landcover map in our project directory came the 
NLCD 2011 data hosted by USGS.  However, RHESSysWorkflows supports the use of
custom landcover maps regsitered via RegisterRaster.  In either case,
we need to provide raster reclassification rules so that
RHESSysWorkflows will know how to generate vegetation, land use,
roads, impervious, and optionally LAI maps from the landcover map.  
To do this, we use the RegisterLandcoverReclassRules tool:

    RegisterLandcoverReclassRules.py -p standard -k

NLCD2011 is a known landcover type in RHESysWorkflows (in addition to NLCD2006),
so all we need do is use the *-k* (a.k.a. *--generateKnownRules*)
option.  For a custom landcover map, we could instead use the *-b*
(a.k.a. *--buildPrototypeRules*) option to generate prototype rules
that we can edit as needed.  It is also possible to specify that
existing reclass rules should be imported from another directory on
your computer using the *-r* (a.k.a. *--ruleDir*) parameter.  To 
include LAI reclass rules when registering prototype or existing 
rules, you must use the *-l* (a.k.a. *--includeLaiRules*) parameter

> The known rules for NLCD2006 and NLCD2011 that ship with RHESSysWorkflows include
> an LAI reclass rules file with values for grassland, and evergreen
> needle leaf and deciduous broadleaf forests (both temperate) drawn 
> from the International Satellite Land Surface Climatology Project II
> (ISLSCP II) project.  These data can be downloaded [here](http://daac.ornl.gov/cgi-bin/dsviewer.pl?ds_id=971).

Whether using known rules, building prototype rules, or importing
existing rules, RegisterLandcoverReclassRules will result in the
following four rules files being created in the *rules* directory of
your project directory:

- stratum.rule
- landuse.rule
- impervious.rule
- road.rule
- lai-recode.rule (if the *--includeLaiRules* option was selected)

There is no need to edit these rules for this NLCD2011 example, but
you should take a moment to look at how these rules work.
RHESSysWorkflows uses GRASS's
[r.reclass](http://grass.osgeo.org/grass64/manuals/r.reclass.html)
command ([r.recode](http://grass.osgeo.org/grass64/manuals/r.recode.html)
for creating LAI maps), and so the rules files follow this format.  
It's important to note that the landcover reclass rules for stratum and 
landuse must result in raster maps whose values labels match class 
names present in the RHESSys ParamDB database.  Thus, be very careful 
in editing the righthand side of the expressions in your stratum and 
landuse reclass rules.

Note that to keep track of edits you make to your project's reclass
rules in your project metadata, you should use the RunCmd workflow
command (see the section on custom workflows to learn how to use this
tool). 

> You can find information on NLCD classes [here](http://www.mrlc.gov/nlcd2011.php)

Once the landcover reclass rules are in place, it is very easy to
generate the raster maps derived from the landcover data as well as
the vegetation and land use definition files needed by RHESSys; this
is done using the following command:

    GenerateLandcoverMaps.py -p standard

> If you would like an LAI map to be generate, you must use the *-l*
> (a.k.a. *--makeLaiMap*) parameter on the above command line. This
> will only work if you are using known landcover reclass rules, or
> if you requested that RegisterLandcoverReclassRules include LAI 
> reclass rules when creating prototype rules or using existing rules. 

Like with the soil texture map and definition generation step,
GenerateLandcoverMaps will provide descriptive output of the
vegetation and land use definition types encountered in the raster
data.

#### Creating the worldfile for a watershed

Now we are almost ready to create the worldfile for our watershed. 
First we must create the template from which the world file will be
created. To do this, we'll use the GenerateWorldTemplate tool. 
Fortunately this is very easy because the metadata store contains 
nearly all the information needed to create the template.  If you are 
using multiple climate stations, and therefore have a base station
map that you created using GenerateBaseStationMap, all you need do
is:

    GenerateWorldTemplate.py -p standard
      
If you are using a single climate station and did not create a climate
station map, you must specify the climate station as follows:

    GenerateWorldTemplate.py -p standard -c bwi

Here we're using the climate station named *bwi*.

In either case, if your workflow is missing any information necessary
for making the world template, GenerateWorldTemplate will exit with
a corresponding error.

> If you want to see the template file generate, as well as other
> information, use the *-v* (a.k.a. *--verbose*) option

Now use the CreateWorldfile tool to create a world file using this 
template:

    CreateWorldfile.py -p standard -v

We've specified the the *-v* (a.k.a. *--verbose*) command line option.
This will print details about what CreateWorldfile, and the programs
it runs on your behalf, is doing.  This is recommended as these
programs can fail in complex ways that CreateWorldfile may not be able
to detect, so you'll likely want to know what's going on under the
hood.

When CreateWorldfile finishes, it will create an initial worldfile
named *worldfile_init* in the *worldfiles* directory in the *rhessys*
directory in your project directory.

#### Creating the flow table

As with worldfile creation, at this point in the workflow,
RHESSysWorkflows's metadata store contains nearly all the information
needed to create a flow table using the createflowpaths (CF) RHESSys
program.  The two choices you have are whether CF should create a flow
table that includes roads and/or includes a surface flow table to
modeling non-topographic routing of rooftops.  We'll route roads in
this example, leaving rooftops for the *custom local data* workflow
discussed below.

Run CreateFlowtable as follows:

    CreateFlowtable.py -p standard --routeRoads

This will result in the creation of a flow table called *world.flow*
in the *flow* directory of your *rhessys* directory.  Now we have
almost everything we need to run RHESSys simulations.

#### Initializing vegetation carbon stores

RHESSys provides a program called LAIread to initialize vegetation
carbon stores in your worldfile.  

> Note, LAIread should only be used for RHESSys simulations with 
> static vegetation (i.e. not dynamic vegetation mode enable via 
> the *-g* command line option to RHESSys).

Initializing carbon stores is a multi-step process that involves 
running LAI read to generate a redefine worldfile, running a 3-day 
RHESSys simulation to incorporate the redefine worldfile, writing 
out a new worldfile with initialized vegetation carbon stores.  
RHESSysWorkflows automates all of these processes for you, it can 
even figure out what date to start the 3-day RHESSys simulation on 
based on your climate data.

> In the current version of RHESSysWorkflows, RunLAIRead is only able
> to read simulation start dates from point time-series climate data.
> Users of ASCII or NetCDF gridded climate data must run LAI read by
> hand.  The next release of RHESSysWorkflows will add support for
> gridded climate data to RunLAIRead.

You can run RunLAIRead as follows:

    RunLAIRead.py -p standard -v

Note that we use the verbose command line option here as well.  The
new GRASS-based version of LAIread is relatively new and not as well
tested, so we advise you to keep a close watch on what it is doing.

LAIread relies on allometric relationships to initialize vegetation
carbon stores.  These allometric parameters have not yet been added to
RHESSys ParamDB.  A default version of the parameters for RHESSys base
vegetation classes is stored in the RHESSys ParamDB source code
[repository](https://github.com/RHESSys/ParamDB/blob/develop/allometry/allometric.txt).
RHESSysWorkflows stores this file under the name *allometric.txt* in
the *allometry* folder of the *ParamDB* of your *rhessys/db* folder.  
You can edit this file to suit your needs before running RunLAIRead.  
Consult the
[RHESSys wiki](https://github.com/RHESSys/RHESSys/wiki) 
for more information on allometric relationships used by LAIread.

When finished, a final worldfile named *world* will be created in the
*worldfiles* directory of your *rhessys* directory.  With this
worldfile, you are ready to perform subsequent model workflow steps
including: spin-up, calibration, scenario runs, and analysis and
visualization.

This concludes this tutorial using RHESSysWorkflows to create a
RHESSys world file and flow table using standard spatial data
infrastructure.

#### Running RHESSys models
We need one more thing before we can run our model, a *TEC file*.
TEC stands for "temporal event controller".  We use a *TEC file*
to tell RHESSys to do things on at certain times during a simulation.  
For example, to redefine the worldfile to simulate timber harvest or 
forest fire. We also use tec files to tell RHESSys what model outputs 
should be produced when.  To create a TEC file that tells RHESSys to 
print daily model outputs starting on 10/1/2008, do the following:

    RunCmd.py -p standard echo "2008 10 1 1 print_daily_on" > standard/rhessys/tecfiles/tec_daily.txt

For more information on tec file format, see the [RHESSys wiki](https://github.com/RHESSys/RHESSys/wiki/Temporal-Event-Control-File-(TEC-file)). 

Once you have built a RHESSys model using RHESSysWorkflows, you can run
your model manually.  However this will not capture information about
model runs in your project metadata.  If you would like to record your
runs in your project metadata, use the RunModel command:

    RunModel.py -v -p standard -d "Test model run" --basin -pre test -st 2008 1 1 1 -ed 2010 10 1 1 -w world -t tec_daily.txt -r world.flow -- -s 0.07041256017 133.552915269 1.81282283058 -sv 4.12459677088 78.3440566535 -gw 0.00736592779294 0.340346799457
    
Notice the '--' in the command line.  All of the command line options before
the '--' are options required by RunModel.py; some of these are also common
RHESSys options.  All of the options after the '--' will be passed to 
RHESSys.  Because the project metadata knows where RHESSys is installed in your
project directory, you don't have to specify the full path of any of the RHESSys input
files (e.g. world files, flow tables, tec files, etc), just specify the filenames.
RunModel will echo RHESSys console outlet to the screen (if the *-v* or verbose
option is specified as above), and will always save the same output into
a file named 'rhessys.out' stored in the output folder for each model run.  The output
folder will be named based on the value you provide for the '-pre' or output prefix
option. 

### Working in watersheds outside the United States

The above standard U.S. spatial data acquisition workflow steps do not
provide access to data outside the U.S. (by definition).  However, it is
still possible to use RHESSysWorkflows to develop RHESSys models for watersheds
outside the U.S.  One option is to use custom local data, which is described
[here](#custom-local-data-workflow).  If you are working in Australia, EcohydroLib 
(and by extension RHESSysWorkflows) provides access to 1-second (~30-meter) resolution 
DEM data (derived from SRTM data) using web services interfaces provided by 
[Geoscience Australia](http://www.ga.gov.au/data-pubs/web-services/ga-web-services).
These data can be accessed using the *GetGADEMForBoundingBox* command.  A typical
workflow would begin as follows.  First, define your study area using the
*RegisterStudyAreaShapefile* command:

    RegisterStudyAreaShapefile.py -p PROJECT_DIR -s /path/to/my/study/area/shapfile.shp
    
(Replace PROJECT_DIR with the name of your EcohydroLib project).

next, extract the bounding box coordinates for your study area:

    GetBoundingboxFromStudyareaShapefile.py -p PROJECT_DIR
    
then, download Geoscience Australia DEM data:

    GetGADEMForBoundingBox.py -p PROJECT_DIR
    
Currently, there are three types of DEM data available:
* 1 second SRTM Digital Elevation Model of Australia
* 1 second SRTM Digital Elevation Model - Hydrologically Enforced
* 1 second SRTM Digital Elevation Model - Smoothed

To acquire the *1 second SRTM Digital Elevation Model of Australia* data,
run *GetGADEMForBoundingBox* as follows:

    GetGADEMForBoundingBox.py -p PROJECT_DIR -d dem_1s

to acquire the *1 second SRTM Digital Elevation Model - Hydrologically Enforced* data:

	GetGADEMForBoundingBox.py -p PROJECT_DIR -d dem_h_1s
	
and to acquire the *1 second SRTM Digital Elevation Model - Smoothed* data:

    GetGADEMForBoundingBox.py -p PROJECT_DIR -d dem_s_1s
    
Consult the [Geoscience Australia metadata catalog](http://www.ga.gov.au/metadata-gateway/metadata/record/gcat_72759)
for more information about these data sets. 

The remainder of your workflow would proceed with importing streamflow gage coordinates
and subsequent steps described [here](#import-streamflow-gage-coordinates). 

In addition to Australia DEM, EcohydroLib provides access to gridded 
soils data provided by CSIRO and availble as part of the 
[Soil and Landscape Grid of Australia](http://www.clw.csiro.au/aclep/soilandlandscapegrid/)
dataset.  To download these data into your project use the
*GetSoilGridAustralia* command:

    GetSoilGridAustralia.py -p PROJECT_DIR
    
This will download a subset of the available gridded Australia
Soils Data from the Australia-wide 3D Soil Attributes dataset; currently
*GetSoilGridAustralia* will download the percent sand, percent silt, 
and percent clay layers.  Data for the first 1-m of the soil profile is
downloaded, and a depth-weighted average value for each pixel is
generated using these layers.  Once these data have been downloaded,
you can use the *GenerateSoilTextureMap* command to generate RHESSys
soil texture map and parameters for USDA soil classes:

    GenerateSoilTextureMap.py -p PROJECT_DIR
    
See [above](#generating-soil-texture-map) for more details.


### Custom local data workflow

The following sections outline how one might use RHESSysWorkflows to
build RHESSys input files using custom data already available on your
computer.  Unlike the above standard spatial data tutorial, we won't
provide data for the workflow steps below.  Instead, we'll describe
how your data should be formatted to work with each workflow tool.
To avoid duplication, only those concepts specific to using local data
in RHESSysWorkflows will be discussed.  You are encouraged to read the
standard spatial data tutorial above as well.  The workflow sequence
covered below is not the only possible workflow involving local data.
Also, it is possible to combine steps from this example workflow with
steps from the standard spatial data tutorial.

#### Import a DEM into your project

When working in watersheds outside the coverage of the NHD (such as
when working outside of the U.S.) the first workflow step is to import
a digital elevation model data using the RegisterDEM tool.  The DEM
to be imported must be in a format readable by
[GDAL](http://www.gdal.org/formats_list.html).  

Run RegisterDEM as follows:

    RegisterDEM.py -p PROJECT_DIR -d /path/to/my/DEM.tif -b "City of Springfield, Custom LIDAR"

To run this command, replace *PROJECT_DIR* with the absolute or
relative path of an empty directory where you would like the data and
metadata for your project to be stored (i.e. your project directory).
It is also possible to reproject or resample the DEM on import.  See
RegisterDEM's help for more information (i.e. run with the *-h*
option).

RegisterDEM will result in the DEM being copied to your project
directory, also the DEM extent will be used to determine the bounding
box for the study area; a polygon of the DEM extent will be generated
and saved as a shapefile in your project directory.

#### Use a DEM with streams and storm drains burned into it

If you are working with an urbanized catchment, it is often necessary
to "burn" streams or storm drains into your DEM so that you can properly
delineate the "sewershed."  RHESSysWorkflows allows you do use both a
"stream burned" and a standard "non-burned" DEM in the same workflow.  
The burned DEM will only be used for operations that require it (e.g.
watershed delineation, flow table creations); the standard DEM will be 
used for determining elevation, slope, aspect, etc.  To use a stream
burned DEM, do the following:

    RegisterRaster.py -p PROJECT_DIR -t stream_burned_dem -r /path/to/my/burnedDEM.tif -b "City of Springfield, Custom LIDAR, storm drain burned with Whitebox GAT 3.1.2"

Once the stream burned raster has been registered with the workflow the
*DelineateWatershed* and *CreateFlowtable* tools will know to use this raster
instead of the standard DEM; all other tools that use the DEM will continue
to use the standard DEM.  If you want to override this behavior (e.g. to
test the effect that the burned DEM has on watershed delineation), you can
pass the *--ignoreBurnedDEM* option to *DelineateWatershed* or *CreateFlowtable*, 
which will cause them to use the standard DEM instead.

> We recommend the excellent open-source [Whitebox GAT](http://www.uoguelph.ca/~hydrogeo/Whitebox/)
> for burning streams into DEM datasets.

#### Import streamflow gage coordinates 

The coordinates of the streamflow gage associated with your watershed
are registered with the workflow using the RegisterGage tool.  The
tool takes as input a point shapefile containing one or more points;
the WGS84 lat-lon coordinates for the desired gage will be extracted
from the shapefile.  These coordinates will be written to the metadata
store, and a new point shapefile containing a point only for the
selected gage will be created in the project directory.

A typical way to run RegisterGage is:

    RegisterGage.py -p PROJECT_DIR -g /path/to/gage/shapefile.shp -l DATASET_NAME -a GAGE_ID_ATTRIBUTE -d GAGE_ID

To run this comment, replace *PROJECT_DIR* as above, specify the input
shapefile you'd like to use, the name of the dataset within the
shapefile, the name of the ID gage attribute in the dataset, and the
ID of the desired gage.  The name of the dataset is usually the same
as the filename of the shapefile (minus the .shp).  If you are unsure,
you can use the command line tool
[ogrinfo](http://www.gdal.org/ogrinfo.html), which ships with GDAL.

#### Importing data into GRASS for use with RHESSys

The following workflow steps are identical whether using standard
spatial data or custom local data and will not be covered here:

- Create a new GRASS location
- Import RHESSys source code into your project
- Import RHESSys climate data
- Delineate watershed and generate derived data products
- Generate landcover maps in GRASS

See the above standard spatial data tutorial for detailed information
on these steps.

#### Importing other raster layers

For a list of all of the current raster map types supported by
EcohydroLib, run the RegisterRaster tool as follows:

    RegisterRaster.py -h

This will also show all of the resampling and other import options
available.

What follows is a series of examples showing how to input some of
these raster types.  All rasters must be stored in a file format
readable by GDAL (see above).

##### Landcover data

    RegisterRaster.py -p PROJECT_DIR -t landcover -r /path/to/my/landcover_map.tif --noresample -b "Baltimore Ecosystem Study LTER" --force

Here we are importing a landcover raster map obtained from the
Baltimore Ecosystem Study LTER where we've asked RegisterRaster not to
resample the raster (unless its spatial reference system differs from
the DEM; i.e. the resolution of the raster cells won't be changed).
We're also telling RegisterRaster to ignore the fact that the extent
of the landcover raster does not exactly match the extent of the
DEM/study area.  After import, you are strongly encouraged to
visualize the landcover map overlaid on the DEM using QGIS to ensure
that the landcover will cover an adequate portion of your study area.

> For landcover maps, we recommend that you do not resample when
> registering the raster using RegisterRaster, but instead let GRASS
> handle the resampling.

To make the landcover map in the project directory available to
RHESSys, it must be imported into GRASS as follows:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t landcover -m nearest

This will import the landcover raster into GRASS, and then resample
the raster using the nearest neighbor method.  For a list of valid
resampling methods, run ImportRasterMapIntoGRASS with the *-h* option;
you may also specify *none* as the resampling method and the raster
will not be resampled.

##### Rooftop connectivity

Starting with RHESSys 5.16, the createflowpaths (CF) utility is able
to create surface flow tables that can incorporate non-topographic
routing of flow from rooftops to nearby impervious and pervious areas.
RHESSys 5.16 can use separate surface and subsurface flow tables to
simulate the effect of such non-topographic routing on the landscape.
You can find more information on using surface flowtable routing in RHESSys
[here](https://github.com/RHESSys/RHESSys/wiki/Surface-Flowtable-Routing).

To import a rooftop connectivity raster, use RegisterRaster as follows:

    RegisterRaster.py -p PROJECT_DIR -t roof_connectivity -r /path/to/my/roof_map.tif --noresample --force

> As with landcover maps, we recommend do not let RegisterRaster
> resample roof connectivity rasters, instead letting GRASS handle the
> resampling.  RegisterRaster uses GDAL to resample rasters.  GDAL
> ignore null/nodata pixels when resampling, whereas GRASS's
> r.resamp.interp does not.  Thus, when a landcover and a roof top
> connectivity raster, which contains nodata values for all non-roof
> pixels, are resampled in RegisterRaster, they can become
> mis-registered, which will result in an invalid surface routing
> table.

Then make your rooftop connectivity raster available for RHESSys by
importing it into GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t roof_connectivity -m nearest

##### Vegetation LAI

As described in the standard spatial data tutorial above,
EcohydroLib/RHESSysWorkflows requires that the user provide their own
LAI data, which can be imported into a project using RegisterRaster:

     RegisterRaster.py -p PROJECT_DIR -t lai -r /path/to/my/lai_map.tif --force

Now make your LAI raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t lai -m none

##### Custom patch map

A custom patch map can be imported into a project as follows:

    RegisterRaster.py -p PROJECT_DIR -t patch -r /path/to/my/patch_map.tif --noresample

Then make your patch raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t patch -m none

##### Custom soils data

A custom soils map can be imported into a project as follows:

    RegisterRaster.py -p PROJECT_DIR -t soil -r /path/to/my/soils_map.tif -b "Brian Miles <brian_miles@unc.edu>, based on field observations"

Then make your soil raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t soils -m none

##### Climate station zone map

The GeneratePatchMap tool will use the patch map as the zone
map.  If you wish to use another map for the zone map, do the
following after running DelineateWatershed:

    RegisterRaster.py -p PROJECT_DIR -t zone -r /path/to/my/zone_map.tif -b "Brian Miles <brian_miles@unc.edu>, climate station zones based on lapse rate"

Then make your zone raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t zone -m none

##### Isohyet map

By default no isohyet map will be used when creating the world file for
a watershed.  If you wish to use an isohyet map, do the following before
running GenerateWorldTemplate:

    RegisterRaster.py -p PROJECT_DIR -t isohyet -r /path/to/my/isohyet_map.tif -b "Brian Miles <brian_miles@unc.edu>, isohyet map"

Then make your isohyet raster available for RHESSys by importing it into
GRASS:

    ImportRasterMapIntoGRASS.py -p PROJECT_DIR -t isohyet -m none --integer

> Note that we tell ImportRasterMapIntoGRASS to transform the isohyet
> raster values to integers on import.  This is necessary due to limitations
> in the current version of the RHESSys tool grass2world.  When doing the,
> integer conversion, ImportRasterMapIntoGRASS wil multiply the raster
> values by 1000, giving three significant digits.  To use another value,
> specify the *--multiplier* option.

#### Generating RHESSys definitions for custom soil data

When using custom soil data with RHESSysWorkflows you need to create
soil definition files before you can create a worldfile.  To create
soil definitions, you must first create raster reclass rules that map
between your soil type and a soil type known to RHESSys ParamDB.  At
present, ParamDB contains definitions drawn from the literature for
USDA soil textures.  However you may load custom soil parameters into
your own local copy of ParamDB.  For more information, see the ParamDB
[README](https://github.com/RHESSys/ParamDB).

To create prototype soil reclass rules for a project, do the following:

    RegisterCustomSoilReclassRules.py -p PROJECT_DIR -b

Here we're using the *-b* (a.k.a. *--buildPrototypeRules*) command
line option.  This will result in the creation of a file called
*soils.rule* in the *rules* directory of your project directory. You
will need to edit this file as necessary to map your custom soil types
to ParamDB soil types.  

> Make sure that the soil class names on the righthand side of each
> reclass rule correspond to soil class names in ParamDB

You can also import existing soil reclass rules as follows:

    RegisterCustomSoilReclassRules.py -p PROJECT_DIR -r /path/to/my/existing/reclass_rules/

The *-r* (a.k.a. *--ruleDir*) parameter must point to a directory that
contains a file named soils.rule.  This will will be copied into the
*rules* directory of your project directory.

Once you have valid soil reclass rules in place, you can generate
RHESSys soil parameter definition files for your custom soils using
the following command:

    GenerateCustomSoilDefinitions.py -p PROJECT_DIR 

This tool will print information to the screen about each soil type
encountered and the RHESSys ParamDB soil parameter classes they map
to.  If you see no such print out, check your soil reclass rule file
to make sure it is correct.  The resulting soil definition files will
be written to the *defs* directory in the *rhessys* directory of your
project directory.

> Remember most RHESSysWorkflows commands support the *--overwrite*
> command line option for overwriting existing data stored in the
> project directory or in GRASS.

#### Creating a world file template in areas with low slope

Due to limitations in the current version of RHESSys's *grass2world*
tool, slope values less than 1.0 will be truncated to 0.0.  This causes
values of NaN (i.e. not a number) to result for the spherical average 
of aspect calculation.  To work around this, you can use the 
*--aspectMinSlopeOne* command line option to instruct
*GenerateWorldTemplate* to use a slope map whose minimum value is 1.0
when calculating the spherical average of aspect:

    GenerateWorldTemplate.py -p PROJECT_DIR --aspectMinSlopeOne -c MY_CLIMATE_STATION1

#### Creating a surface flow table using a roof connectivity map

If you are using a roof connectivity map in your workflow, you need to
explicitly tell CreateFlowtable to use the roof connectivity map to
generate a surface flow table.  Do so as follows:

    CreateFlowtable.py -p PROJECT_DIR --routeRoofs --routeRoads

Here we're using both the *--routeRoofs* and *--routeRoads* options.
You are not required to use both together, but usually when modeling
rooftop connectivity you will be working in a watershed that also has
roads whose effects on routing you will also want to consider.

#### Creating the worldfile and initializing vegetation carbon stores

The following workflow steps are identical whether using standard
spatial data or custom local data and will not be covered here:

- Creating the worldfile for a watershed
- Initializing vegetation carbon stores

See the above standard spatial data tutorial for detailed information
on these steps.

#### Running custom commands

RHESSysWorkflows provides many tools for preparing RHESSys models, 
however there are many possible other tools and workflow steps
that can be used to build a model.  To allow arbitrary commands
to be carried out on data stored in a project directory, 
RHESSysWorkflows provides the RunCmd command, for example you
may which to edit your worldfile template and then re-run *grass2world*
by hand:

    RunCmd.py -p PROJECT_DIR cp PROJECT_DIR/rhessys/templates/template PROJECT_DIR/rhessys/templates/template.orig
    RunCmd.py -p PROJECT_DIR emacs PROJECT_DIR/rhessys/templates/template
    export PATH=PROJECT_DIR/rhessys/bin:${PATH}
    RunCmd.py -p PROJECT_DIR PROJECT_DIR/rhessys/bin/g2w ...
    
(it is necessary to manually add your project directory's copy of the
RHESSys binaries to your path because grass2world runs a helper program
called *rat* that must be in your path)
    
Although RHESSysWorkflows will not be able to capture full metadata
about the input and output files used and produced by commands run
through RunCmd, it will write an entry to the processing history
of your project metadata.  This way, you at least have a record of the
custom workflow steps you applied to the data in your project directory.

#### Creating multiple worldfiles based on subbasins

For large model domains, it may be desirable to break up your watershed
into multiple worldfiles.  RHESSysWorkflows allows you to do this using
the *CreateWorldfileMultiple* command:

    CreateWorldfileMultiple.py -p PROJECT_DIR

This will create one worldfile for each subbasin delineated for your
watershed.

Once you've created multiple worldfiles, you can create corresponding
flow tables using the *CreateFlowtableMultiple* command:

    CreateFlowtableMultiple.py -p PROJECT_DIR
    
*CreateFlowtableMultiple* supports the same command line options as
its counterpart *CreateFlowtable*.

Finally, you can initialize vegetation carbon and nitrogen stores
for multiple worldfiles using *RunLAIReadMultiple*:

    RunLAIReadMultiple.py -p PROJECT_DIR


Appendix
--------

### Visualizing RHESSys output

RHESSysWorkflows includes tools to visualize RHESSys model output.

> Note that these tools are still in development, but beta versions
> are provided for your convenience; functionality and options may
> change without notice.

The first tool, *RHESSysPlot*, will produce plots for basin-scale
variables such as streamflow.  This tool is very flexible, and includes
the ability to plot observed data vs. modeled data, and to plot data
for multiple simulations.  A prototypical usage to plot observed and
simulated hydrographs with rainfall plotted on a second y-axis is as 
follows:

	RHESSysPlot.py --plottype standard -o PATH_TO_OBSERVED -d PATH_TO_SIMULATION/rhessys_basin.daily -c streamflow --secondaryData PATH_TO_SIMULATION/rhessys_basin.daily --secondaryColumn precip --secondaryLabel "Rainfall (mm/day)" -t "DR5 streamflow" -l "Test simulation" -f test_plot --figureX 8 --figureY 3 -y "Streamflow (mm/day)" --color magenta

> Go [here](https://drive.google.com/file/d/0B7aK-9pTSLS-Q0JDeE4wQmN2VVU/edit?usp=sharing) 
> to download example observed streamflow for the DR5 study catchment 
> used in the first part of this tutorial

The *--figureX* and *--figureY* options control the size of the plot (in
inches).  RHESSysPlot also allows you to make standard time series, semi-log 
scale timeseries, and cumulative distribution function plots. For a full 
description of options, use the *--help* option:

    RHESSysPlot.py --help
    
In addition to making static plots of basin-scale output variables, 
RHESSysWorkflows provides a tool, *PatchToMovie*, for making animations 
of patch-scale output variables.  To use this tool, you first need to 
have RHESSys simulations for which patch-scale output was created 
(e.g. using the *-p* output option).  The following example will create
a 30-frames-per-second animation for infiltration:

    PatchToMovie.py -p PROJECT_DIR -d PATH_TO_SIMULATION_WITH_PATCH_OUTPUT/rhessys_patch.daily -o OUTPUT_DIRECTORY -f OUTPUT_FILENAME -v "recharge * 1000.0" --mask GRASS_RASTER_LAYER --overlay GRASS_RASTER_LAYER_1 [GRASS_RASTER_LAYER_N] --fps 30 -t "infiltration"

Note that the variable can be an aribitrary mathematical expression
(using '+', '-', '*', and '/') combining patch-level RHESSys variable 
names as well as numerical constants (as in the example).  When using
such expressions, you'll want to specify a title for each frame in your
animation using the *-t* (a.k.a. *--mapTitle*) option (otherwise the expression
will be used as the title, which likely won't fit on the frame). 

When specifying simulation output (e.g. *-r*) and the GRASS mapset (e.g. *-g*),
it is important to use the same GRASS mapset that was used to create the
worldfile used to run the simulation.

For a full description of options, use the *--help* option:

    PatchToMovie.py --help  
    
*PatchToMovie* uses a command line program called *ffmpeg* to encode
individual maps into a movie file.  To install *ffmpeg* do the following:

#### OS X
- Install [Homebrew](http://brew.sh)
- Install *ffmpeg*:

    brew install ffmpeg

#### Linux (Debian/Ubuntu-based systems)
- Install *ffmpeg* (and *vlc* for viewing animations):

    sudo apt-get install ffmpeg vlc
    
Lastly, you must add an entry to your EcohydroLib configuration file.  For
OS X:

    [RHESSYS]
    PATH_OF_FFMPEG = /usr/local/bin/ffmpeg
    
For Linux:

    [RHESSYS]
    PATH_OF_FFMPEG = /usr/bin/ffmpeg

See [Setup EcohydroLib and RHESSysWorkflows configuration file](#setup-ecohydrolib-and-rhessysworkflows-configuration-file)
for more details on setting up your configuration file.

### Deprecated installation instructions

#### OS X 10.7 through 10.10 using Kyngchaos GIS packages

##### Install Xcode (OS X developer tools):
- Install Xcode via the App Store

- Launch Xcode

- Make sure that Xcode command line tools are installed by running the
  following from the command line (e.g. using the Terminal app):

```
xcode-select --install
```

- Agree to the Xcode license by running the following command (we only
    run this command to force Xcode show us the license): sudo cc
    
##### Install GIS tools: GRASS & QGIS
Note, GRASS version 6.4 is required for RHESSysWorkflows (GRASS 7.0 is not
supported at this time).  GRASS is used internally to carry out workflow 
steps (leading to the creation of RHESSys world files and flow tables).  
You will also find it useful to use GRASS to visualize the results from 
some workflow steps.

> Before installing GRASS, etc. under OS X 10.8, 10.9 or 10.10, you
> will need to enable applications from any source to be installed.
> To do so open *System Preferences > Security & Privacy > General*
> and choose "Allow apps downloaded from: Anywhere". Doing so exposes
> your computer to more security risks from downloaded software. We
> recommend that you revert this setting once you are finished with
> installation.

To install GRASS on OS X, visit http://www.kyngchaos.com/software/grass

Here you will need to download and install the following:

1. GDAL Complete framework
2. FreeType framework
3. cairo framework
4. PIL (Python imaging library)
5. GRASS.app

While you are there, we recommend you also install QGIS (Quantum GIS)

In addition to GRASS and components installed above, install:

1. NumPy from http://www.kyngchaos.com/software/python
2. SciPy from http://www.kyngchaos.com/software/python
2. Matplotlib Python module from http://www.kyngchaos.com/software/python
3. QGIS from from http://www.kyngchaos.com/software/qgis

QGIS is useful for visualizing output for earlier workflow steps that precede the importing data into GRASS. 

##### Install RHESSysWorkflows Python modules (including EcohydroLib) 
Before installing RHESSysWorkflows, we need to install some
dependencies by hand (this is annoying, but unavoidable):

    sudo pip install pandas patsy

This is necessary because another depdendency (statsmodels) requires
that we install its dependencies first. If you are running XCode 5.1 or later, 
you may encounter this error:

    clang: warning: unknown argument: '-mno-fused-madd' [-Wunused-command-line-argument-hard-error-in-future]
    clang: note: this will be a hard error (cannot be downgraded to a warning) in the future
    clang: warning: argument unused during compilation: '-mno-fused-madd'
    
If you don't see the above error, skip the next step.  To work around
the error, install statsmodels' dependencies this way (you'll probably
want to copy and paste this rather than typing it):

    sudo ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install pandas patsy
    
This too is annoying, but is unaviodable (for now).

To install RHESSysWorkflows and its dependencies (including EcohydroLib), 
enter the following from your Terminal if you are running XCode 5.0 or earlier:

    sudo pip install rhessysworkflows

If you are running Xcode 5.1 (but not Xcode 6.1 or later), we need to
set the ARCHFLAGS variable as above:

	sudo ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install rhessysworkflows

Again, only do the above step if youa re running Xcode 5.1, not Xcode 6.1.

This may take a while as several of the modules rely on non-Python
code that has to be compiled.
    
> Why are GDAL Python libraries not included as a dependency of
> RHESSysWorkflows? This is to make life easier for users of OS X 10.7
> and 10.8.  For these OSes, the GDAL complete installer that
> accompanies GRASS will install GDAL Python modules in the copy of
> Python 2.7 that ships with the OS, and the GDAL Python module does
> not successfully build by itself under OS X, which would make the
> rhessysworkflows install fail.  Linux users will have to make sure
> they install GDAL Python modules in addition to GDAL itself
> (e.g. via a companion package, or by 'sudo pip install GDAL').

##### Install GRASS Addons for RHESSysWorkflows
Follow these steps to install the GRASS addons needed by RHESSysWorkflows:

1. First start GRASS
 - Double-click on the *GRASS-6.4* icon in your Applications folder

2. Create a new location (it doesn't matter where, we'll only use it to run
the g.extension command to install the extensions)
3. Install r.soils.texture

    g.extension extension=r.soils.texture

4. Install r.findtheriver

    g.extension extension=r.findtheriver

5. Exit GRASS

For more information on these addons (r.soils.texture and r.findtheriver), see:
- [r.findtheriver](http://grasswiki.osgeo.org/wiki/AddOns/GRASS_6#r.findtheriver)
and r.soils.texture
- [r.soils.texture](http://grasswiki.osgeo.org/wiki/AddOns/GRASS_6#r.soils.texture).

##### Setup EcohydroLib and RHESSysWorkflows configuration file
- Download a [prototype configuration](https://raw.github.com/selimnairb/RHESSysWorkflows/master/docs/config/ecohydro-OSX.cfg) file.

- Save into a file named '.ecohydro.cfg' stored in your home directory
and replace all occurances of *&lt;myusername&gt;* with your user name
(To find out your OS X user name, use the *whoami* command in
Terminal).
    
- Set ECOHYDROLIB_CFG environment variable so that RHESSysWorkflows
  can find your configuration file

    + From Terminal, do the following:

		echo "export ECOHYDROLIB_CFG=${HOME}/.ecohydro.cfg" >> ~/.bash_profile

    + Re-load bash profile (or close and open a new Terminal window):

		source ~/.bash_profile

This concludes installation and configuration instructions for OS X
10.7 through 10.10 using Kyngchaos GIS packages.

#### OS X 10.6
Apple, and thus many third-party software developers, no longer
supports OS X 10.6.  If you are still running OS X 10.6, you may want
to explore [upgrade
options](http://arstechnica.com/apple/2014/03/snow-leopard-updates-are-probably-done-here-are-your-os-x-upgrade-options/)
as many older Macs can run newer operating systems, upto and including
the latest version.  If your Mac still has some life in it, it is
important to upgrade from OS X 10.6 this version is no longer
receiving security updates from Apple, and because newer versions have
more security features by design.

If you wish to install RHESSysWorkflows on OS X 10.6, follow the
instructions below (though we no longer have a OS X 10.6 machine to
test on, so we won't be able to help if you run into problems).

Due to its age, there are a few more installation steps needed under
OS X 10.6.  Also, once Apple stops support this version of the OS,
support for OS X 10.6 will also be dropped from subsequent releases of
RHESSysWorkflows.  If you were thinking of upgrading from OS X 10.6 to
10.9 for other reasons, this may add another.

> You will need to use the *sudo* command line tool to install many of
> the components needed for EcohydroLib/RHESSysWorkflows.  The sudo
> command allows you to run other commands as a super user.  Under OS
> X, by default, only users who are 'admins' have permission to run
> sudo.  To check if your user account is an administrator, or to make
> your user an administrator open *System Preferences > Users &
> Groups*.  Note that to use sudo, your account will also have to have
> a non-blank password.  See this Apple support
> [article](http://support.apple.com/kb/HT4103?viewlocale=en_US&locale=en_US)
> for more information.

##### Download and install Python 2.7 from: http://www.python.org/download/

Once installation has completed, make sure that Python 2.7 is the
default Python version by doing the following from the Terminal:

    python
    
This will load the Python interpreter.  The first line of output will
display the Python version number.  Type *exit()* to exit the
interpreter.

##### Download setuptools from: https://pypi.python.org/pypi/setuptools/0.8
Install setuptools as follows:
1. Unpack the archive by double-clicking on it in Finder
2. From Terminal:

    cd setuptools-0.8
    sudo python ez_setup.py

##### Install Xcode (OS X developer tools)
1. Download and install Xcode 3.2.6 and iOS SDK 4.3 for Snow Leopard
[here](https://developer.apple.com/downloads/index.action) (This
requires you to register for a free developer account)

2. Download and install Git from http://git-scm.com/download/mac

RHESSysWorkflows uses Git to download RHESSys source code so you don't have to.

##### Install PIP, a tool for installing Python modules
Pip is the recommended way to install Python modules (i.e. rather than
using easy_install). For example, Pip allows you to easily uninstall
modules.  To install pip, enter the following in a Terminal window:

    sudo easy_install pip

##### Install GIS tools: GRASS & QGIS
Note, GRASS version 6.4 is required for RHESSysWorkflows (GRASS 7.0 is not
supported at this time).  GRASS is used internally to carry out workflow 
steps (leading to the creation of RHESSys world files and flow tables).  
You will also find it useful to use GRASS to visualize the results from 
some workflow steps.

To install GRASS on OS X, visit http://www.kyngchaos.com/software/grass

Here you will need to download and install the following:

1. GDAL Complete framework
2. FreeType framework
3. cairo framework
4. PIL (Python imaging library)
5. GRASS.app

While you are there, we recommend you also install QGIS (Quantum GIS)

In addition to GRASS and components installed above, install:

1. NumPy from http://www.kyngchaos.com/software/python
2. SciPy from http://www.kyngchaos.com/software/python
2. Matplotlib Python module from http://www.kyngchaos.com/software/python
3. QGIS from from http://www.kyngchaos.com/software/qgis

QGIS is useful for visualizing output for earlier workflow steps that precede the importing data into GRASS. 

##### Install GDAL Python modules
Even though we installed the GDAL complete framework above, we still
need to install the GDAL Python modules for the copy of Python 2.7 we
installed above; the GDAL framework only installs the Python modules
for Python 2.6, which RHESSysWorkflows is not compatible with. These
installation steps are a little ugly, but bear with me (or upgrade
from OS X 10.6). From a Terminal window type the following:

    export PATH=${PATH}:/Library/Frameworks/GDAL.framework/unix/bin
    sudo pip install --no-install GDAL
    cd /tmp/pip-build-root/GDAL
    sudo python setup.py build_ext --include-dirs=/Library/Frameworks/GDAL.framework/Headers --library-dirs=/Library/Frameworks/GDAL.framework/Versions/Current/unix/lib
    sudo pip install --no-download GDAL

##### Install RHESSysWorkflows Python modules (including EcohydroLib) 
Before installing RHESSysWorkflows, we need to install some
dependencies by hand (this is annoying, but unavoidable):

    sudo pip install pandas patsy

This is necessary because another depdendency (statsmodels) requires
that we install its dependencies first. 

To install RHESSysWorkflows and its dependencies (including EcohydroLib), 
enter the following from your Terminal if you are running XCode 5.0 or earlier:

    sudo pip install rhessysworkflows

##### Install GRASS Addons for RHESSysWorkflows
Follow these steps to install the GRASS addons needed by RHESSysWorkflows:

1. First start GRASS
 - Double-click on the *GRASS-6.4* icon in your Applications folder

2. Create a new location (it doesn't matter where, we'll only use it to run
the g.extension command to install the extensions)

3. Install r.soils.texture

    g.extension extension=r.soils.texture

4. Install r.findtheriver

    g.extension extension=r.findtheriver

5. Exit GRASS

For more information on these addons (r.soils.texture and r.findtheriver), see:
- [r.findtheriver](http://grasswiki.osgeo.org/wiki/AddOns/GRASS_6#r.findtheriver)
and r.soils.texture
- [r.soils.texture](http://grasswiki.osgeo.org/wiki/AddOns/GRASS_6#r.soils.texture).

##### Setup EcohydroLib and RHESSysWorkflows configuration file
- Download a [prototype configuration](https://raw.github.com/selimnairb/RHESSysWorkflows/master/docs/config/ecohydro-OSX_10.6.cfg) file.

- Save into a file named '.ecohydro.cfg' stored in your home directory
	Replace all occurances of *&lt;myusername&gt;* with your user name (To find
	out your OS X user name, use the *whoami* command in Terminal).
    
- Set ECOHYDROLIB_CFG environment variable so that RHESSysWorkflows
  can find your configuration file

    + From Terminal, do the following:

		echo "export ECOHYDROLIB_CFG=${HOME}/.ecohydro.cfg" >> ~/.bash_profile

	+ Re-load bash profile (or close and open a new Terminal window):

		source ~/.bash_profile

This concludes installation and configuration instructions for OS X 10.6.

### Install local data
RHESSysWorkflows allows you to use local copies of the National
Hydrography Dataset Plus (NHD Plus) to locate USGS streamflow gages,
and the National Landcover Dataset (NLCD 2006). If you will be building
many models across the U.S. or are running RHESSysWorkflows in a 
server environment and would like to minimize calls to external web
services, you may wish to install these datasets locally to improve
performance.  *This is entirely optional.  Most users can ignore this
as querying webservices for these data is preferable to downloading
and installing these relatively large datasets.*
 
#### Setup NLCD2006 data
To setup a local copy of NLCD2006 land cover data, do the following:
- Download NLCD2006 data [here](https://docs.google.com/file/d/0B7aK-9pTSLS-MHRrRTVVRV9zdVk/edit?usp=sharing)

    It is important that you download this version of the dataset, and
    not the official data from http://www.mrlc.gov/nlcd06_data.php.
    The offical data are packaged using a version of PkZip that is not
    compatible with OS X's GUI or commandline unzip utilities.

- Copy NLCD2006 archive to the parent folder where you would like to store it

    For example, under OS X, create a folder called 'data' in your
    home directory

- Unpack NLCD2006 data (this will take a while...time for a coffee break):
    
    + OS X 10.6: From the command line:
    
      tar xvjf nlcd2006_landcover_4-20-11_se5.tar.bz2
        
    + OS X 10.7/10.8: double-click on the archive in Finder

#### Setup pre-packaged NHDPlusV2 data
If you want to setup a local copy of NHDPlusV2 data you can obtain
these data by downloading all or a subset of the NHDPlusV2 data and
building the database as described in the [EcohydroLib
documentation](https://github.com/selimnairb/EcohydroLib).
Alternatively, you can download a pre-built copy of the NHDPlusV2
database needed by RHESSysWorkflows
[here](https://docs.google.com/file/d/0B7aK-9pTSLS-dGVzWGRCd1NwNzQ/edit?usp=sharing).
To download and unpack the pre-built data, do the following:

- Download pre-packaged NHDPlusV2 database [here](https://docs.google.com/file/d/0B7aK-9pTSLS-dGVzWGRCd1NwNzQ/edit?usp=sharing)

    Note, the compressed data are nearly 7 GB, nearly 11 GB
    uncompressed, the download may take a while

- Copy the pre-packaged NHDPlusV2 database archive to the parent
  folder where you would like to store it
    
    For example, under OS X, create a folder called 'data' in your
    home directory

- Unpack NHDPlusV2 database archive (this will take a while...have a
    cup of tea) 

    + OS X 10.6: From the command line:
    
        tar xvjf NHDPlusV2.tar.bz2
        
    + OS X 10.7/10.8: double-click on the archive in Finder
    
 ### Setup EcohydroLib and RHESSysWorkflows configuration file for local data
 
- Choose the appropriate prototype configuration file:

    + [OS X 10.6](https://raw.github.com/selimnairb/RHESSysWorkflows/master/docs/config/ecohydro-OSX_10.6-local.cfg)

    + [OS X 10.7/10.8](https://raw.github.com/selimnairb/RHESSysWorkflows/master/docs/config/ecohydro-OSX-local.cfg)
    
    + [Linux](https://raw.github.com/selimnairb/RHESSysWorkflows/master/docs/config/ecohydro-Linux-local.cfg)

- Save into a file named '.ecohydro.cfg' stored in your home directory
	Replace all occurances of '<myusername>' with your user name (To find
    out your OS X or Linux user name, use the *whoami* command in Terminal).

- Modify the example configuration to point to your NHDPlusV2 and
  NLCD2006 local data [if you are using these data]:

    If you are using OS X, and if you placed the data in a directory
    called 'data' in your home directory, the only changes you need to
    make is to substitute '<myusername>' with your user name.   
    
    If you chose to store local NLCD or NHDPlusV2 somewhere else, simply
    use the absolute path of each file. 
    
- Set ECOHYDROLIB_CFG environment variable so that RHESSysWorkflows
  can find your configuration file

    For example, under OS X, from Terminal, do the following:

	+ Open your bash profile in an editor:

		nano ~/.bash_profile

	+ Add the following at the end of the file:

		export ECOHYDROLIB_CFG=${HOME}/.ecohydro.cfg

	+ Save the file

	+ Re-load bash profile (or close and open a new Terminal window):

		source ~/.bash_profile
