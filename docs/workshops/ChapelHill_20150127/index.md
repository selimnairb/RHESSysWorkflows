# RHESSys Workshop - January 27-28, 2015


For this workshop, we will be using [RHESSysWorkflows](https://github.com/selimnairb/RHESSysWorkflows) to build a RHESSys model for the [Baisman Run](http://waterdata.usgs.gov/md/nwis/uv/?site_no=01583580) watershed, a forested and suburban watershed near Baltimore Maryland, and is one of the [study watersheds](http://www.umbc.edu/cuere/BaltimoreWTB/data.html) of the Baltimore Ecosystem Study Long-Term Ecological Research site ([BES LTER](http://www.beslter.org)).

We will discuss applications of RHESSys to urban and forested watersheds.  The [agenda](#agenda) includes time for discussion and small group/individual work.  Please come prepared to ask questions relevant to your study site.  Also, there will be some time to work on your own model, so bring along any data you might need to build a RHESSys model for your study site.  Please refer to the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#using-rhessysworkflows---introduction) or the RHESSys [wiki](https://github.com/RHESSys/RHESSys/wiki) for more information on data requirements.

## Logistics

#### Where
The workshop will be held at the offices of the Institute for the Environment at the University of North Carolina at Chapel Hill.  These offices are located in the Europa Center, the address of which is:
 
100 Europa Drive, Suite 490  
Chapel Hill, NC 27517

Suite 490, the Institute for the Environment (IE) offices, is located just to the left of the elevators on the 4th floor.

#### When
Tuesday January 27th and Wednesday January 28, 2015 from 9:00 AM to 5:00 PM

#### Food
This is a free workshop therefore breakfast and lunch will not be provided, however light snacks and coffee will be provided during our afternoon breaks.  There is a restaurant in the Europa Center that is open for lunch and serves high-quality southern fare.  There are grocery stores, coffee, and bagel shops within a short drive of the Europa Center.

#### What to bring
Unfortunately, we are enable to provide computers for you to use during the workshop.  Please come with your own laptop computer to use.  You will need a machine with at least 4 GB of memory to run the virtual machine we will use (8 GB or more is recommended; see below).

## Table of contents
- [Before you arrive](#before-you-arrive)
- [Agenda](#agenda)
- [Workshop tutorials](#workshop-tutorials)
	- [Acquiring geospatial data using EcohydroLib](#acquiring-geospatial-data-using-ecohydrolib)	
	- [Building RHESSys input files using RHESSysWorkflows](#building-rhessys-input-files-using-rhessysworkflows)
	- [Running RHESSys and visualizing output](#running-rhessys-and-visualizing-output)
	- [Model calibration with RHESSysCalibrator](#model-calibration-with-rhessyscalibrator)

### Before you arrive
We will be using some basic Unix commands as part of this workshop.  To make this go more smoothly, we recommend that novice Unix users review lessons 1-3 of the Software Carpentry [Unix Shell lessons](http://software-carpentry.org/v5/novice/shell/index.html).

Before taking part in this workshop, you will need to use the following instructions to download and install a virtual machine that has RHESSysWorkflows pre-installed.The virtual machine requires at least 10 GB of disk space once installed.  To run the virtual machine, your computer should have at least 4 GB of memory (8 GB or more is recommended).If you have any questions, please contact brian_miles@unc.edu.

#### Install VirtualBox
To run the RHESSysWorkflows virtual machine, you will need to first download and install VirtualBox version 4.3.20 or later from:[https://www.virtualbox.org/](https://www.virtualbox.org/)Make sure to also install the "VirtualBox 4.3.20 Oracle VM VirtualBox Extension Pack" (or the version that matches your VirtualBox version), available from the VirtualBox download page.
#### Install 7-Zip [Windows only]
Before you can install the RHESSysWorkflows virtual machine under a Windows host operating system, you must install a utility that can open the archive format used to compress the virtual machine (this compression is necessary to save cloud storage space and to reduce download times).  We suggest you install 7-Zip, which you can find here:

[http://www.7-zip.org/](http://www.7-zip.org/)#### Download RHESSysWorkflows virtual machine
Download the compressed virtual machine acrhive here:

[http://goo.gl/qkSxuv](http://goo.gl/qkSxuv)

The compressed file is about 2 GB, so we recommend you download via a fast network or when you have a lot of time.  When the download completes, move the archive, named “RHESSysWorkflows-VM-201501.tbz” to your “VirtualBox VMs” directory (this will be in your home directory under OS X).

#### Uncompress RHESSysWorkflows virtual machine##### WindowsRight-click on “RHESSysWorkflows-VM-201501.tbz” and choose to uncompress using 7-Zip.
##### OS X (from Finder)We do not recommend you uncompress the VM archive using Finder (i.e. by double clicking on the .tbz file); use Terminal instead (see below).##### OS X (from Terminal) or under Linux
Un-archive the virtual machine using tar:    tar xvf RHESSysWorkflows-VM-201501.tbz#### Run RHESSysWorkflows virtual machine1.	Open the uncompressed virtual machine using the “Machine > Add…” menu:
	a.	Navigate to “RHESSysWorkflows 201501.vbox” and click “Open”2.	Click on “Start” in the VirtualBox Manager3.	When the virtual machine (VM) finishes booting, you will automatically be loged in.  If the VM, you will need the password:
	a.  Username: rhessys	b.	Password: rhessys### Agenda
#### Tuesday, January 27
**9:00 a.m. – 9:45 a.m. – RHESSys conceptual overview***9:45 a.m. – 10:00 a.m. – BREAK***10:00 a.m. – 12:00 p.m. – RHESSys model development with RHESSysWorkflows***12:00 p.m. – 1:30 p.m. – LUNCH***1:30 p.m. – 3:00 p.m. – RHESSys model development with RHESSysWorkflows (cont’d)***3:00 p.m. – 3:15 – BREAK***3:15 p.m. – 5:00 – Visualizing RHESSys output data**#### Wednesday, January 28
**9:00 a.m. – 10:45 p.m. – Model calibration with RHESSysCalibrator***10:45 a.m. – 11:00 a.m. – BREAK***11:00 a.m. – 12:00 p.m. – Model calibration with RHESSysCalibrator (cont'd)***12:00 p.m. – 1:30 p.m. – LUNCH***1:30 p.m. – 3:00 p.m. – Discussion / small-group work***3:00 p.m. – 3:15 – BREAK***3:15 p.m. – 5:00 – Discussion / small-group work**## Workshop tutorials
A typical workflow will consist of running data
processing/registration tools from EcohydroLib.  Once the required
datasets are in place (e.g. DEM, soils, landcover, etc.)
RHESSysWorkflows tools can be run to create the world file and flow
table needed to run a RHESSys model.

> If at any point during this workshop you fall behind or experience a problem and cannot continue with the instructions, you can find finished version of all of the workflow and all products in the *completed* directory within the *rhessys* directory of your desktop.

All EcohydroLib and RHESSysWorkflows tools are executed from the
command line.  Each tool stores the data and metadata associated
with a single workflow in a directory, called a *project directory*.
Metadata are stored in a file in the project directory called
*metadata.txt*.  There can only be one metadata.txt in a project
directory, so it is essential that each workflow have its own project
directory.

Each workflow tool will print usage information when run on its own
for example running:

    GetNHDStreamflowGageIdentifiersAndLocation.py 

Will yield:

    usage: GetNHDStreamflowGageIdentifiersAndLocation.py [-h] [-i CONFIGFILE] -p
    PROJECTDIR -g GAGEID
    GetNHDStreamflowGageIdentifiersAndLocation.py: error: argument -p/--projectDir is required

This indicates that the -p (a.k.a. --projectDir) argument is required; that is, you must specify the project directory associated with workflow for which you are running the tool.  For many EcohydroLib/RHESSyWorkflows tools, this is the only required command
line parameter.  

It's good practice when running a command to first execute the command with no command line arguments.  This will show you the required and optional parameters.  To get detailed help for a given command, run the command with the -h (a.k.a. --help) argument, for example:

    GetNHDStreamflowGageIdentifiersAndLocation.py -h
 
Note that while this particular tool, and RHESSysWorkflows tools
in general, have long names, they are long to be descriptive so as to
be easier to use.  To avoid having to type these long names out, you
are encouraged to make use of *tab* completion in Terminal.  To use
tab completion, simply type the first few characters of a command and
then hit the 'tab' key on your keyboard; the entire command name will
be 'completed' for you on the command line.  If the entire name is not 'completed' for you, hit tab again to see that list of commands that match what you've typed so far.  Once you type enough characters to uniquely identify the command, hitting tab once more will complete the command name.
### Acquiring geospatial data using EcohydroLib

#### Create an empty RHESSysWorkflows project
First, make an empty RHESSysWorkflows project called *Baisman_10m* in the *rhessys* directory on your desktop by entering the following commands in a terminal window:

	cd Desktop/rhessys
    mkdir Baisman_10m

#### Import Digital Elevation Model data
For this workshop we will mostly be using custom datasets stored locally, instead of U.S. national geospatial data acquired from web services interfaces.  One exception is soils data, which we will acquire from USDA SSURGO web services.  The local data for this workshop are stored in the *Baisman_data* directory stored in the *rhessys* directory on the desktop.

We will import digital elevation model (DEM) data using the *RegisterDEM* tool.  The DEM to be imported must be in a format readable by [GDAL](http://www.gdal.org/formats_list.html).  

Run *RegisterDEM* as follows:

    RegisterDEM.py -p Baisman_10m -d Baisman_data/BR_1km_DEM_10m_fillpits_breachpits_breachdepressions.tif -b "brian_miles@unc.edu; Derived from BES 2006 LIDAR data"
    
(remember to use the *tab* key to complete long file names and reduce typing)

*RegisterDEM* will result in the DEM being copied to your project
directory, and the DEM spatial resolution will determine the default spatial resolution of your project (i.e. other rasters imported to your project will by default be resampled to the match the DEM resolution and spatial reference).  Also, the DEM extent will be used to determine the bounding
box for the study area; a polygon of the DEM extent will be generated
and saved as a shapefile in your project directory.

You can view the newly imported DEM using QGIS (if QGIS is not install, *sudo aptitude install qgis* will install it.)

#### Import streamflow gage coordinates 
We will use the *RegisterGage* tool to tell EcohydroLib the coordinates of the Baisman Run streamflow gage.  This tool takes as input a point shapefile containing one or more points; the WGS84 lat-lon coordinates for the desired gage will be extracted from the shapefile.  These coordinates will be written to the metadata store, and a new point shapefile containing a point only for the selected gage will be created in the project directory.

Run *RegisterGage* as follows:

    RegisterGage.py -p Baisman_10m -g Baisman_data/BR_gage_UTM_WGS84.shp -l BR_gage_UTM_WGS84 -a StationID -d 1583580
    
For more information on how RegisterGage works, consult the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#import-streamflow-gage-coordinates).

#### Download soils data from SSURGO
The USDA NRCS provides the [Soil Data
Mart](http://soildatamart.nrcs.usda.gov), a sophisticated web
services-based interface for querying and downloading high-resolution
SSURGO soils data.  SSURGO data are structured as a complex database
consisting of both spatial and tabular data.  For more information on
this database format and the soil survey data exposed through the
SSRUGO database please see the [SSURGO
metadata](http://soildatamart.nrcs.usda.gov/SSURGOMetadata.aspx).

For more information see the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#download-soils-data-from-ssurgo).

To download SSURGO features and attributes for Baisman Run, run the
following command:

    GetSSURGOFeaturesForBoundingbox.py -p Baisman_10m
    
The download should take a few seconds, and may sometimes fail if the Soil Data Mart web services are down for maintenance.  Once the download completes, you can view the downloaded soils data by opening *MapunitPolyExtended.shp* in QGIS.

Now would be a good time to open the *metadata.txt* file in your project directory to explore the metadata and provenance information for your project so far.

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

    GenerateSoilPropertyRastersFromSSURGO.py -p Baisman_10m

Later on, we'll use the percent sand and percent clay rasters to generate a USDA soil texture map, which we'll use to define RHESSys soil parameters for our study watershed.

#### Importing landcover data
We'll use the *RegisterRaster* command to import landcover data into our project:

    RegisterRaster.py -p Baisman_10m -t landcover -r Baisman_data/LandCover_BACO_2007_BR_1km_UTM_WGS84.tif -b "brian_miles@unc.edu; Extracted from 2007 BES 7-class 2-ft LC"

By default, *RegisterRaster* will resample the raster it is importing (landcover in this case) to match the spatial reference and resolution of the DEM.  For more information, see the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#landcover-data).

For our example model for Baisman Run, we'll use the landcover data to generate the remaining geospatial data needed by RHESSys: vegetation type, land use type, impervious surfaces, roads, and vegetation leaf area index.

This concludes the data acquisition portion of this tutorial.  We'll use the geospatial data, in generic formats, that we acquired using EcohydroLib as input to RHESSysWorkflows tools; RHESSysWorkflows will compose and transform these generic data into the input files -- world file, flow table, vegetation and other parameters -- needed to run RHESSys.

### Building RHESSys input files using RHESSysWorkflows

#### Create a new GRASS location 
RHESSys requires that all spatial data used to create a world file and
flow table for a RHESSys model be stored in a GRASS GIS mapset.  We'll
start building these data in RHESSysWorkflows by creating a new GRASS
location and mapset within our project directory, and importing our
DEM into this mapset:

    CreateGRASSLocationFromDEM.py -p Baisman_10m -d "10-m res. RHESSys model for USGS 01583580 BAISMAN RUN AT BROADMOOR, MD"
    
> You can use the *--overwrite* option to CreateGRASSLocationfromDEM to
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
code from GitHub using the *ImportRHESSysSource* tool.  However, this
tool is also capable of importing RHESSys source code stored on your
computer.  This allows you to import the code from a previous
RHESSysWorkflows project; ParamDB is always downloaded from GitHub,
even when RHESSys source code is imported from a local source.

To download ParamDB and the RHESSys source code and store them in your
project directory issue the following command:

    ImportRHESSysSource.py -p Baisman_10m

If you want to checkout an alternate branch, use the *-b* option to 
specify the Git branch of RHESSys to use (e.g. 'develop'). By default, 
*ImportRHESSysSource* will use the *master* branch, which is the appropriate 
branch to use with RHESSys 5.18.
	
Once *ImportRHESSysSource* finishes importing RHESSys source code into
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
Because of the great variability of climate data formats, and the
complexity of time-series workflows, we have chosen to focus
development effort on RHESSysWorkflows toward making it easier to
acquire and manipulate geospatial data required for building RHESSys
work files and flow tables.  This means that the modeler is
responsible for building the climate data necessary for building
RHESSys world files and performing model runs.  

RHESSysWorkflows provides the *ImportClimateData* tool to import
RHESSys climate data into your project:

    ImportClimateData.py -p Baisman_10m -s Baisman_data/br_composite-clim
    
*ImportClimateData* should indicate that it imported the climate station named *br_composite*.

For more information about using *ImportClimateData* see the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#import-rhessys-climate-data).  To learn about how to use multiple climate stations in a RHESSys model, see [the following](https://github.com/selimnairb/RHESSysWorkflows#create-climate-stations-map).

#### Delineate watershed and generate derived data products
RHESSysWorkflows automates the process of delineating your study
watershed based on the location of the streamflow gage registered in
the workflow using EcohydroLib.  As part of this process, many datasets needed by RHESSys will be derived from the DEM.  To delineate the watershed:

    DelineateWatershed.py -p Baisman_10m -t 500 -a 3.8

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
RHESSysWorkflows provides *GeneratePatchMap*, an automated tool for
creating gridded and clumped patch maps.  Gridded patch maps consist
of a regular grid of the same resolution and extent as the DEM;
clumped maps can be created using elevation or topographic wetness
index rasters.  Modelers can also use custom patch maps registered via
EcohydroLib's *RegisterRaster* tool and imported into GRASS using
*ImportRasterMapIntoGRASS*.  We'll use a simple gridded patch map:

    GeneratePatchMap.py -p Baisman_10m -t grid
    
For information on other patch map types, see the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#generating-a-patch-map).

#### Generating soil texture map
Since we used EcohydroLib's SSURGO tools to generate percent sand
and percent clay raster maps for our watershed, we can use the GRASS
add-on r.soils.texture to generate USDA soil texture classes, for which
RHESSys's ParamDB contains parameters.  It is also possible to use
custom soil maps (refer to the [tutorial](https://github.com/selimnairb/RHESSysWorkflows#generating-rhessys-definitions-for-custom-soil-data)).

To generate our soil texture map in GRASS, as well as the corresponding RHESSys soil definition files, use the *GenerateSoilTextureMap* tool as follows:

    GenerateSoilTextureMap.py -p Baisman_10m

As it runs, this command will print information about what soil texture classes were encountered in the soil texture map, and what RHESSys soil
default IDs these classes map onto.  You can view the resulting soil
texture map (named *soil_texture*) in GRASS.  The soil definition
files will be stored in the *defs* directory of the *rhessys* directory
stored in your project directory.

#### Generate derived landcover maps
RHESSysWorkflows uses a single landcover map to generate the following maps
used by RHESSys:

- Vegetation type (stratum)
- Land use
- Roads
- Impervious surfaces
- Leaf area index (LAI; optional, which we'll use in this tutorial)

The first step in generating these maps is to import the landcover
raster from your project directory into GRASS:

    ImportRasterMapIntoGRASS.py -p Baisman_10m -t landcover -m nearest

Visualize landcover map in GRASS and set colors as follows:

    1 0:128:0
	2 green
	3 yellow
	4 blue
	5 magenta
	6 black
	7 grey

For more information on supported landcover types please refer to the [tutorial](https://github.com/selimnairb/RHESSysWorkflows#generate-landcover-maps-in-grass). 

Next, we need to provide raster reclassification rules so that
RHESSysWorkflows will know how to generate vegetation, land use,
roads, impervious, and LAI maps from the landcover map.  
To do this, we use the *RegisterLandcoverReclassRules* tool:

    RegisterLandcoverReclassRules.py -p Baisman_10m -b --includeLaiRules

Here the *-b* (a.k.a. *--buildPrototypeRules*) option is used to 
generate prototype rules that we can edit as needed.  To include 
LAI recode rules when registering prototype or existing rules, also 
specify the *-l* (a.k.a. *--includeLaiRules*) option.

As run above, *RegisterLandcoverReclassRules* will result in the
following four rules files being created in the *rules* directory of
your project directory:

- stratum.rule
- landuse.rule
- impervious.rule
- road.rule
- lai-recode.rule

We will edit each of these files so that RHESSysWorkflows creates the
correct maps for each map type.  First, it's useful to understand a
little about how these maps are made.  RHESSysWorkflows uses GRASS's
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

Edit the landcover to impervious surface re-classification rule (this 
will use the graphical text editor named *mousepad*):

	RunCmd.py -p Baisman_10m mousepad Baisman_10m/rules/impervious.rule
	
Make the impervious surface rule look like:

	5 6 7 = 1 impervious
	* = 0 pervious

Edit the land use rule:

	RunCmd.py -p Baisman_10m mousepad Baisman_10m/rules/landuse.rule
	
Make the land use rule look like:

	1 thru 4 = 1 undeveloped
	5 thru 7 = 3 urban
	
Edit the road rule:

	RunCmd.py -p Baisman_10m mousepad Baisman_10m/rules/road.rule
	
Make the road rule look like:

	6 = 1 road
	* = NULL
	
Edit the vegetation stratum rule:

	RunCmd.py -p Baisman_10m mousepad Baisman_10m/rules/stratum.rule

Make the stratum rule look like:

	3 thru 7 = 4 nonveg
	2 = 32 lawn_5cm
	1 = 21 deciduous_BES
	
Edit the leaf area index recode rule:

	RunCmd.py -p Baisman_10m mousepad Baisman_10m/rules/lai-recode.rule
	
Make the recode rule look like:

    1:1:4.0
	2:2:1.5
	3:7:0.0

Once the landcover reclass rules are in place, it is very easy to
generate the raster maps derived from the landcover data as well as
the vegetation and land use definition files needed by RHESSys:

    GenerateLandcoverMaps.py -p Baisman_10m --makeLaiMap

Like with the soil texture map and definition generation step,
GenerateLandcoverMaps will provide descriptive output of the
vegetation and land use definition types encountered in the raster
data.

#### Creating the world file for a watershed
Now we are almost ready to create the world file for our watershed. 
First we must create the template from which the world file will be
created. To do this, we'll use the *GenerateWorldTemplate* tool. 
Fortunately this is very easy because the metadata store contains 
nearly all the information needed to create the template:

    GenerateWorldTemplate.py -p Baisman_10m -c br_composite --aspectMinSlopeOne
    
The *-c* (a.k.a. *--climateStation*) option specifies the climate 
station to associate with this world file template.  The 
*--aspectMinSlopeOne* option is necessary work around limitations
in the program used to create the world file when the input DEM has 
areas of low slope as is present in Baisman Run (see [here](https://github.com/selimnairb/RHESSysWorkflows#creating-a-world-file-template-in-areas-with-low-slope) for more information).

You can view the resulting template, which is located in the *templates*
directory of the *rhessys* directory in your project directory *Baisman_10m*,
using a text editor.

Now use the *CreateWorldfile* tool to create a world file using this 
template:

    CreateWorldfile.py -v -p Baisman_10m

We've specified the the *-v* (a.k.a. *--verbose*) command line option.
This will print details about what *CreateWorldfile*, and the programs
it runs on your behalf, is doing.  This is recommended as these
programs can fail in complex ways that *CreateWorldfile* may not be able
to detect, so you'll likely want to know what's going on under the
hood.

When *CreateWorldfile* finishes, it will create an initial world file
named *worldfile_init* in the *worldfiles* directory in the *rhessys*
directory in your project directory. 

We recommend that you check your world file for missing or invalid 
geographic variables before proceeding.  We'll use the Unix command
*grep* to do this:

    grep -i nan Baisman_10m/rhessys/worldfiles/world_init
    
This will print out any lines that contain *nan* (which stands for
"not a number").  If your world file does not contain any such lines
no output will be produced.  If there are *nan* values in your world
review the above workflow steps to make sure that each step was executed
properly.  One obvious source of *nan* values is forgetting to 
specify the *--aspectMinSlopeOne* option to *GenerateWorldTemplate* tool.

#### Creating the flow table
As with worldfile creation, at this point in the workflow,
RHESSysWorkflows's metadata store contains all the information
needed to create a flow table using the *createflowpaths* (CF) RHESSys
program.  We'll use *CreateFlowtable* to create our flow table:

    CreateFlowtable.py -v -p Baisman_10m

This will result in the creation of a flow table called *world.flow*
in the *flow* directory of your *rhessys* directory.  Now we have
almost everything we need to run RHESSys simulations.  

See the RHESSysWorkflows tutorial to learn how to [route surface flows for road pixels directly to the stream](https://github.com/selimnairb/RHESSysWorkflows#creating-the-flow-table) and [create surface flow tables using a roof connectivity map](https://github.com/selimnairb/RHESSysWorkflows#creating-a-surface-flow-table-using-a-roof-connectivity-map).

As with the world file, we recommend you check your flow table for
any invalid values using the *grep* tool:

    grep -i nan Baisman_10m/rhessys/flow/world.flow
    
You should see no output if your flow table does not contain invalid
values.

#### Initializing vegetation carbon and nitrogen stores
RHESSys provides a program called *LAIread* to initialize vegetation
carbon and nitrogen stores in your world file.  

> Note, *LAIread* should only be used for RHESSys simulations with 
> static vegetation (i.e. not dynamic vegetation mode enable via 
> the *-g* command line option to RHESSys).

Initializing carbon and nitrogen stores is a multi-step process 
that involves  running LAI read to generate a redefine worldfile, 
running a 3-day RHESSys simulation to incorporate the redefine 
worldfile, writing out a new worldfile with initialized vegetation 
carbon and nitrogen stores.  RHESSysWorkflows automates all of 
these processes for you using the tool *RunLAIRead*, which can 
even figure out what date to start the 3-day RHESSys simulation on 
based on your climate data.

> In the current version of RHESSysWorkflows, RunLAIRead is only able
> to read simulation start dates from point time-series climate data.
> Users of ASCII or NetCDF gridded climate data must run LAI read by
> hand.  The next release of RHESSysWorkflows will add support for
> gridded climate data to RunLAIRead.

To initialize vegetation carbon and nitrogen stores, *LAIread* relies 
on allometric relationships between leaf area and carbon and nitrogen 
mass in various plant tissues (e.g. leaf, stem, root).  Consult the
[RHESSys wiki](http://wiki.icess.ucsb.edu/rhessys/Defining_stratum_state_variables_from_LAI_(lairead)) for more 
information on allometric relationships used by LAIread.  These 
allometric parameters have not yet been added to the RHESSys ParamDB 
database proper.  A default version of the parameters for RHESSys 
base vegetation classes is stored in the RHESSys ParamDB source code[repository](https://github.com/RHESSys/ParamDB/blob/develop/allometry/allometric.txt).  RHESSysWorkflows stores this file under the name *allometric.txt* in the *allometry* folder of the *ParamDB* of your 
*rhessys/db* folder.  

Before we can run *RunLAIRead*, we must edit *allometric.txt* by hand:

    RunCmd.py -p Baisman_10m mousepad Baisman_10m/rhessys/db/ParamDB/allometry/allometric.txt
    
Change the vegetation IDs of the second and third vegetation classes
to match the stratum IDs used in our project; 2 becomes 21 (i.e. deciduous_BES), and 3 becomes (i.e. lawn_5cm).  Also change the specific
leaf area for lawn_5m frin 17.0 to 32.0 (i.e. change the second value on
the third line).  The resulting *allometric.txt* should look as follows:

    4
    1 8.2 1.2 2.2 0.22 0.16 45.0 139.7 200.0 333.33
    21 32.0 1.2 2.2 0.22 0.16 25.0 48.0 48.0 333.33
    32 32.0 1.2 2.2 0.22 0.16 27.7 47.8 250.0 333.33
    4 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0 0.0

Now you can run *RunLAIRead* as follows:

    RunLAIRead.py -v -p Baisman_10m

When finished, a final worldfile named *world* will be created in the
*worldfiles* directory of your *rhessys* directory.  With this
worldfile, you are ready to perform subsequent model workflow steps
including: spin-up, calibration, scenario runs, and analysis and
visualization.

This concludes this tutorial using RHESSysWorkflows to create a
RHESSys world file and flow table for the Baisman Run watershed.  Next 
we'll run the model and visualize model output.

### Running RHESSys and visualizing output

#### Creating a RHESSys TEC file
We need one more thing before we can run our model, a *TEC file*.
TEC stands for "temporal event controller".  We use a *TEC file*
to tell RHESSys to do things on at certain times during a simulation.  
For example, to redefine the worldfile to simulate timber harvest or 
forest fire.  We also use TEC files to tell RHESSys what model outputs 
should be produced when.  To create a TEC file that tells RHESSys to 
print daily model outputs starting on 1/1/2007, do the following:

    RunCmd.py -p Baisman_10m echo "2007 1 1 1 print_daily_on" > Baisman_10m/rhessys/tecfiles/tec_daily.txt

For more information on tec file format, see the [RHESSys wiki](https://github.com/RHESSys/RHESSys/wiki/Temporal-Event-Control-File-(TEC-file)). 

#### Running RHESSys models
Once you have built a RHESSys model using RHESSysWorkflows, you are 
free to run your model manually.  However this will not capture information about model runs in your project metadata.  If you would like to record your
runs in your project metadata, use the *RunModel* command:

    RunModel.py -v -p Baisman_10m -d "Test run without calibration" --basin -pre test -st 2007 1 1 1 -ed 2013 10 1 1 -w world -t tec_daily.txt -r world.flow
   
Because the project metadata knows where RHESSys is installed in your
project directory, you don't have to specify the full path of any of the RHESSys input files (e.g. world files, flow tables, TEC files, etc), you 
only need to specify the filenames.  RunModel will echo RHESSys console 
outlet to the screen (if the *-v* or verbose option is specified as above), and will always save the same output into a file named 'rhessys.out' stored 
in the output folder for each model run.  The output folder will be named based on the value you provide for the '-pre' or output prefix
option.  Model output is stored in the *output* directory of the *rhessys*
directory of your project directory.

For more details on using *RunModel* see the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#running-rhessys-models).

#### Visualizing model output
RHESSysWorkflows includes several tools to visualize RHESSys model output.
These tools operate on RHESSys output from the entire watershed (i.e.
basin scale) as well as from individual patches (i.e. patch scale). Since
the model run we just completed was run at the basin scale, we'll look
at basin-scale output first.

> Note that these visualization tools are still in development, but beta versions are provided for your convenience; functionality and options may change without notice.

##### Basin-scale output of daily data
As an initial step to model evaluation we can look partitioning between streamflow and evapotranspiration in RHESSys model output.  We use the 
command *RHESSysPlotMassbalance* to do this:

    RHESSysPlotMassbalance.py -n test_massbalance -o Baisman_data/RHESSys_USGS_01583580_Baisman-20070101_20130930.txt -d Baisman_10m/rhessys/output/test/rhessys_basin.daily -t "Massbalance - Baisman 10-m no-calibration test" --figureX 8 --figureY 6 --color

This will produce PDF and PNG files named *test_massbalance* (as specified
by the *-n* option).  The title of the figure is specified by the *-t* option.
RHESSys basin-scale daily output for our test model run is stored in the file
*rhessys_basin.daily* within the directory *test* in the RHESSys output 
directory.

Next, we can use the *RHESSysPlot* command to plot individual RHESSys basin-scale output variables in a variety of figure types, including in the follow example time series:

    RHESSysPlot.py --plottype standard -o Baisman_data/RHESSys_USGS_01583580_Baisman-20070101_20130930.txt -d Baisman_10m/rhessys/output/test/rhessys_basin.daily -c sat_def_z --secondaryData Baisman_10m/rhessys/output/test/rhessys_basin.daily --secondaryColumn precip --secondaryLabel "Rainfall (mm/day)" -t "Baisman depth to saturated zone" -l "Test simulation" -f test_plot_satdefz --figureX 8 --figureY 3 -y "Sat. def. z (mm)" --color magenta --supressObs
    
Here we're plotting the depth to the saturated zone (i.e. sat_def_z as specified with the *-c* option) with precipitation plotted on a secondary axis.  The depth to the saturated zone is important to look at when debugging a model as before the soil water state variables have been adequately "spun up" (all model state variables start at 0), sat_def_z will be very high.  As the model spins up, the sat_def_z  should decrease more or less monotonically until the soil water stores reach dynamic equilibrium, at which point transient dynamics in water table depth should be seen, with sat_def_z decreasing with precipitation events or seasonally in response to accumulated recharge during leaf-off period.

Next, let's look at a time series of streamflow:

    RHESSysPlot.py --plottype standard -o Baisman_data/RHESSys_USGS_01583580_Baisman-20070101_20130930.txt -d Baisman_10m/rhessys/output/test/rhessys_basin.daily -c streamflow --secondaryData Baisman_10m/rhessys/output/test/rhessys_basin.daily --secondaryColumn precip --secondaryLabel "Rainfall (mm/day)" -t "Baisman streamflow" -l "Test simulation" -f test_streamflow --figureX 8 --figureY 3 -y "Streamflow (mm/day)" --color magenta
    
This serves as a basis of comparison for this plot of log-transformed streamflow, which we specify by changing the *--plottype* option from *standard* to *logy*:

    RHESSysPlot.py --plottype logy -o Baisman_data/RHESSys_USGS_01583580_Baisman-20070101_20130930.txt -d Baisman_10m/rhessys/output/test/rhessys_basin.daily -c streamflow --secondaryData Baisman_10m/rhessys/output/test/rhessys_basin.daily --secondaryColumn precip --secondaryLabel "Rainfall (mm/day)" -t "Baisman streamflow" -l "Test simulation" -f test_streamflow --figureX 8 --figureY 3 -y "Streamflow (mm/day)" --color magenta
    
We can just as easily plot the empirical cumulative distribution function of streamflow by specifying *cdf* as the plot type:

    RHESSysPlot.py --plottype cdf -o Baisman_data/RHESSys_USGS_01583580_Baisman-20070101_20130930.txt -d Baisman_10m/rhessys/output/test/rhessys_basin.daily -c streamflow --secondaryData Baisman_10m/rhessys/output/test/rhessys_basin.daily --secondaryColumn precip --secondaryLabel "Rainfall (mm/day)" -t "Baisman streamflow" -l "Test simulation" -f test_streamflow --figureX 8 --figureY 3 -y "Streamflow (mm/day)" --color magenta
    
In addition to plotting a single variable from a single model run, *RHESSysPlot* can output a scatter plot comparing a variable from two RHESSys model runs.  This is done by setting the plot type to *scatter* and then specifying a second model output file to the *-d* option:

    RHESSysPlot.py --plottype scatter -o Baisman_data/RHESSys_USGS_01583580_Baisman-20070101_20130930.txt -d Baisman_10m/rhessys/output/test/rhessys_basin.daily Baisman_10m/rhessys/output/test/rhessys_basin.daily -c streamflow -t "Baisman streamflow" -l "Test streamflow (mm/day)" "Test streamflow (mm/day)" -f test_streamflow --figureX 8 --figureY 6

For illustration purposes, we are comparing output for a given model run to itself.  It is also possible to produce a scatter plot of log-transformed variable.  This is done by setting the plot type to *scatter-log*:

    RHESSysPlot.py --plottype scatter-log -o Baisman_data/RHESSys_USGS_01583580_Baisman-20070101_20130930.txt -d Baisman_10m/rhessys/output/test/rhessys_basin.daily Baisman_10m/rhessys/output/test/rhessys_basin.daily -c streamflow -t "Baisman streamflow" -l "Test streamflow (mm/day)" "Test streamflow (mm/day)" -f test_streamflow --figureX 8 --figureY 6

There are many other options made available by RHESSysPlot (e.g. setting the legend text as specified above using the *-l* option).  You can learn more about these options by specifying the *--help* option:

    RHESSysPlot.py --help

##### Patch-scale output of yearly data
To visualize RHESSys output at the patch scale, we must first have a model run
with patch-level output.  Enabling patch-level output, especially daily output, results in large output files being generated.  For this example (i.e. so that we don't run out of disk space in our virtual machine) we will run
RHESSys again, this time producing patch-level output each year of the model 
run, instead of daily output.  To be able to do this, we'll need a TEC file
specifying yearly output:

    RunCmd.py -p Baisman_10m echo "2007 1 1 1 print_yearly_on" > Baisman_10m/rhessys/tecfiles/tec_yearly.txt
    
Then to run the model with patch-level output, we specify the *--patch* 
option to *RunModel* instead of the *--basin* model:

	RunModel.py -v -p Baisman_10m -d "Test run without calibration, patch yearly output" --patch -pre test_patch_yearly -st 2006 1 1 1 -ed 2008 1 1 1 -w world -t tec_yearly.txt -r world.flow
	
Note: to reduce model run time for this example, we'll run the model for two years instead of roughly seven years.  Once the model run completes, we can use the *PatchToMap* tool to create a map of an output variable of choice:

	PatchToMap.py -p Baisman_10m -d Baisman_10m/rhessys/output/test_patch_yearly/rhessys_patch.yearly --mask basin --patchMap patch -y 2007 -v 'Qout-Qin' -n test_patch_net_qout_2007
	
Patch-level yearly output is stored in the file named *rhessys_patch.yearly* in the output directory for the model run (i.e. *test_patch_yearly*).  Here note that we are specifying a simple arithmetic expression (i.e. subtraction
of two variables) to serve as the data to be mapped, however it is also possible to map single variables as well.  

To view the patch map open the raster map named *test_patch_net_qout_2007* in GRASS.

### Model calibration with RHESSysCalibrator
Basic RHESSys model calibration is typically performed by calibrating the model's soil parameters against basin-level streamflow using a Monte Carlo approach.  These soil parameters are described in detail [here](https://github.com/RHESSys/RHESSys/wiki/Calibrating-and-running-RHESSys).  The tool [RHESSysCalibrator](https://github.com/selimnairb/RHESSysCalibrator) is used to automate and manage the calibration process, including post-processing steps such as model fitness calculations, as well as GLUE uncertainty analysis.  In the demo that follows we'll demonstrate a simple calibration and post-processing workflow.

RHESSysCalibrator is a system for managing calibration sessions consisting of one or more runs of a RHESSys.  A session contains many runs, each run represents a distinct and uniformly random set of model parameters.  
RHESSysCalibrator uses a database (sqlite3) to keep track of each 
session and run.  The program handles launching and management of each
run, and will update its database as run jobs are submitted, begin
running, and finish (either with or without error).

RHESSysCalibrator is able to launch model runs in parallel on a single computer, or using High Throughput Computing (HTC) clusters running the LSF job scheduling system.


The first step to using RHESSysCalibrator is to create empty 
RHESSysCalibrator project:

    mkdir Baisman_10m_calib
    rhessys_calibrator.py -b Baisman_10m_calib --create

Then, use the provided *rw2rc.py* script to copy your RHESSysWorkflows 
project into the empty RHESSysCalibrator project:

    ./rw2rc.py -p Baisman_10m -b Baisman_10m_calib
    
Next copy observed streamflow data for Baisman Run into the RHESSysCalibrator project:

    cp Baisman_data/RHESSys_USGS_01583580_Baisman-20070101_20130930.txt Baisman_10m_calib/obs
    
RHESSysCalibrator uses a file called *cmd.proto* to control how calibration runs are created.  Edit Baisman_10m_calib/cmd.proto to look like:

    $rhessys -st 2006 1 1 1 -ed 2013 10 1 1 -b -t $tecfile -w $worldfile -r $flowtable -pre $output_path -s $s1 $s2 $s3 -sv $sv1 $sv2 -gw $gw1 $gw2
    
Here we are setting the start and end dates of the calibration runs, as well as setting the soil parameters to calibrated against.  In this case for each model run the following parameters will be varied: vertical decay of saturated hydraulic conductivity for later exchanges (s1 or m in model parlance); lateral saturated hydraulic conductivity (s2 or Ksat0); soil depth (s3); vertical decay of saturated hydraulic conductivity (sv1 or m_v); vertical saturated conductivity (sv2 or Ksat0_v); bypass flow from detention storage directly to hillslope groundwater (gw1); loss from the saturated zone to hillslope groundwater (gw2).

In general, you should only change the start and end dates, and which calibration parameters to include.  Ignore all other parts of cmd.proto as these will be filled in by RHESSysCalibrator for each model run created.
    
For this example, we're not going to use the above cmd.proto, but will make a test cmd.proto to reduce model run time.  It is also useful to create such a test cmd.proto when testing models running in HTC environments:

    cp Baisman_10m_calib/cmd.proto Baisman_10m_calib/cmd.proto.test
    
Edit cmd.proto.test to look like:

	$rhessys -st 2007 1 1 1 -ed 2007 2 1 1 -b -t $tecfile -w $worldfile -r $flowtable -pre $output_path -s $s1 $s2 $s3 -sv $sv1 $sv2 -gw $gw1 $gw2
	
Save cmd.proto so that we don't overwrite it:

    cp Baisman_10m_calib/cmd.proto Baisman_10m_calib/cmd.proto.run
    
Copy cmd.proto.test to cmd.proto:

	cp Baisman_10m_calib/cmd.proto.test Baisman_10m_calib/cmd.proto
	
To run RHESSysCalibrator, we use the *rhessys_calibrator* command:

	rhessys_calibrator.py -b Baisman_10m_calib -p 'Baisman Run 10-m model' -n 'Debug calibration' -i 1 -j 1 --parallel_mode process
	
The *-b* option specifies the RHESSyCalibrator project directory to use.  We describe the project with the *-p* option, and provide notes for this particular calibration session with the *-n* option.  As this is a test calibration session, we specify that we only want to run one iteration using the *-i* option, and that we only want to run at most one model run at a given time using the *-j*.  Lastly, we set the parallel mode to *process*, which is appropriate for running on a laptop or workstation (otherwise RHESSysCalibrator will think you are running in an HTC environment).  For details about these and other options, run *rhessys_calibrator* with the *--help* option.

While running, RHESSysCalibrator will print lots of ugly messages to the screen to tell you want it is doing.  After the calibration session finishes (i.e. once all the model runs, just one in this case, have complete), which should take a few minutes for our test calibration session, we can run *rhessys_calibrator_postprocess* to calculate model fitness parameters (e.g. Nash-Sutcliffe Efficiency for daily streamflow and daily log(streamflow)):

    rhessys_calibrator_postprocess.py -b Baisman_10m_calib -f RHESSys_USGS_01583580_Baisman-20070101_20130930.txt -s 1 --enddate 2007 2 1 1 --figureX 8 --figureY 6
    
The *-s* option specifies the calibration session for which we wish to calculate fitness parameters; the session is *1* as this is our first calibration session for this calibration project.  Also we had to specify the end date of the time period over which we wish to calculate fitness parameters; this is done using the *--enddate* option.  Note that you can specify the temporal aggregation with which to calculate fitness parameters using the *-p* (a.k.a. *--period*) option.  The default is 'daily', but 'weekly' and 'monthly' are also supported.

Once post-processing is finished, the sensitivity of each parameter will be illustrated in "dotty plot" figure output as PNG file named *dotty_plots_SESSION_1_daily.png* stored in the calibration project directory.
    
You can see the parameters used for each calibration run, as well as the fitness values for each run, by opening the calibration SQLite database stored in the calibration project.  We recommend that you use the SQLite Manager add-on in the FireFox web browser to do so.  The calibration database for our project can be found here:

    Baisman_10m_calib/db/calibration.db
    
This concludes this brief RHESSysCalibrator tutorial.