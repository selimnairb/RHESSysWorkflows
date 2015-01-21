# RHESSys Workshop - January 27-28, 2015


For this workshop, we will be using [RHESSysWorkflows](https://github.com/selimnairb/RHESSysWorkflows) to build a RHESSys model for the [Baisman Run](http://waterdata.usgs.gov/md/nwis/uv/?site_no=01583580) watershed, a forested and suburban watershed near Baltimore Maryland, and is one of the [study watersheds](http://www.umbc.edu/cuere/BaltimoreWTB/data.html) of the Baltimore Ecosystem Study Long-Term Ecological Research site ([BES LTER](http://www.beslter.org)).

We will discuss applications of RHESSys to urban and forested watersheds.  The [agenda](#agenda) includes time for discussion and small group/individual work.  Please come prepared to ask questions relevant to your study site.  Also, there will be some time to work on your own model, so bring along any data you might need to build a RHESSys model for your study site.  Please refer to the RHESSysWorkflows [tutorial](https://github.com/selimnairb/RHESSysWorkflows#using-rhessysworkflows---introduction) or the RHESSys [wiki](https://github.com/RHESSys/RHESSys/wiki) for more information on data requirements.

## Logistics

#### Where
The workshop will be held at the offices of the Institute for the Environment at the University of North Carolina at Chapel Hill.  These offices are located in the Europa Center, the address of which is:
 
100 Europa Drive, Suite 490  
Chapel Hill, NC 27517

#### When
9:00 AM to 5:00 PM

#### Food
This is a free workshop therefore meals will not be provided.  There is a restaurant in the Europa Center that is open for lunch and serves high-quality southern fare.  There are grocery stores, coffee, and bagel shops within a short drive of the Europa Center.

## Table of contents
- [Before you arrive](#before-you-arrive)
- [Agenda](#agenda)

### Before you arrive
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
Un-archive the virtual machine using tar:    tar xvf RHESSysWorkflows-VM-201501.tbz#### Run RHESSysWorkflows virtual machine1.	Open the uncompressed virtual machine using the “Machine > Add…”:
	a.	Navigate to “RHESSysWorkflows 201501.vbox” and click “Open”2.	Click on “Start” in the VirtualBox Manager3.	When the virtual machine (VM) finishes booting, you will automatically be loged in.  If the VM, you will need the password:
	a.  Username: rhessys	b.	Password: rhessys### Agenda
#### Tuesday, January 27
**9:00 a.m. – 9:45 a.m. – RHESSys conceptual overview***9:45 a.m. – 10:00 a.m. – BREAK***10:00 a.m. – 12:00 p.m. – RHESSys model development with RHESSysWorkflows***12:00 p.m. – 1:30 p.m. – LUNCH***1:30 p.m. – 3:00 p.m. – RHESSys model development with RHESSysWorkflows (cont’d)***3:00 p.m. – 3:15 – BREAK***3:15 p.m. – 5:00 – Visualizing RHESSys output data**#### Wednesday, January 28
**9:00 a.m. – 10:45 p.m. – Model calibration with RHESSysCalibrator***10:45 a.m. – 11:00 a.m. – BREAK***11:00 a.m. – 12:00 p.m. – Model calibration with RHESSysCalibrator (cont'd)***12:00 p.m. – 1:30 p.m. – LUNCH***1:30 p.m. – 3:00 p.m. – Discussion / small-group work***3:00 p.m. – 3:15 – BREAK***3:15 p.m. – 5:00 – Discussion / small-group work**