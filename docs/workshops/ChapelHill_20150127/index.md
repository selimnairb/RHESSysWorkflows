# RHESSys Workshop - January 27-28, 2015
## Logistics

#### Location
Institute for the Environment  
University of North Carolina at Chapel Hill 
 
100 Europa Drive, Suite 490  
Chapel Hill, NC 27517

#### Time
9:00 AM to 5:00 PM

### Table of contents
**[Before you arrive](#before-you-arrive)**

### Before you arrive
For this workshop, we will be using RHESSysWorkflows, which you can learn more about [here](https://github.com/selimnairb/RHESSysWorkflows).

Before taking part in this training, you will need to use the following instructions to download and install a virtual machine that has RHESSysWorkflows pre-installed.The virtual machine requires at least 10 GB of disk space once installed.  To run the virtual machine, your computer should have at least 4 GB of memory (8 GB or more is recommended).If you have any questions, please contact brian_miles@unc.edu.

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
Un-archive the virtual machine using tar:    tar xvf RHESSysWorkflows-VM-201501.tbz#### Run RHESSysWorkflows virtual machine1.	Open the uncompressed virtual machine using the “Machine > Add…”	a.	Navigate to “RHESSysWorkflows 201501.vbox” and click “Open”2.	Click on “Start” in the VirtualBox Manager3.	When the virtual machine (VM) finishes booting, you will automatically be loged in.  If the VM, you will need the password:	a.  Username: rhessys	b.	Password: rhessys