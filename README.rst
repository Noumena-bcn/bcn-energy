BCN ENERGY - Data Analytics

Software setup for running ENERGY-BCN files

Index:

1 - Download and install the following software, plugins and libraries

2 - Setup an environment with Anaconda

3 - Detailed instruction to install Ladybug + Honeybee

4 - Download the folder with the files

5 - Open the files and adjust the paths

6 - Resources

____________________________________________________________________________

1 - Download and install the following software, plugins and libraries: 

Main Software: 
Rhino + Grasshopper 

Plugins:  

Ladybug & Honeybee 

https://www.food4rhino.com/app/ladybug-tools

Version:  Ladybug 0.0.67 and Honeybee 0.0.64 [Legacy Plugins]
How to install: (please follow the detailed instructions to install it) 


Anemone

https://www.food4rhino.com/app/anemone

Version: Anemone 0.4 2015-Dec-14
How to install: (classical installation) 


GH_CPython 

https://www.food4rhino.com/app/ghcpython

Version: GH_CPython v0.1-alpha 2017-Nov-28
How to install: (classical installation) 
Extra: github


TTtoolbox

https://www.food4rhino.com/app/tt-toolbox

Version: TT Toolbox 1.9 2017-May-25
How to install: (classical installation) 


__________________________________________________________________________

2-Setup an environment with Anaconda : 

Create virtual environments for python with conda.
How to setup a virtual environments using conda for the Anaconda Python distribution
A virtual environment is a named, isolated, working copy of Python that that maintains its own files, directories, and paths so that you can work with specific versions of libraries or Python itself without affecting other Python projects. Virtual environments make it easy to cleanly separate different projects and avoid problems with different dependencies and version requirements across components. The conda command is the preferred interface for managing installations and virtual environments with the Anaconda Python distribution. 

Resume:

- Download Anaconda

- Check conda is installed and available

- Update conda if necessary

- Create a virtual environment

- Activate a virtual environment

- Install additional python packages

- Deactivate a virtual environment

- Delete a virtual environment



Download Anaconda 

 https://docs.continuum.io/anaconda/install/windows/

Check conda is installed and in your PATH
Open a terminal client.
Enter conda -V into the terminal command line and press enter.
If conda is installed you should see something like the following.
$ conda -V
conda 3.7.0

- Check conda is up to date
In the terminal client enter
conda update conda
Update any packages if necessary by typing y to proceed.

- Create a virtual environment for your project
In the terminal client enter the following where “yourenvname” is the name you want to call your environment, and replace “x.x” with the Python version you wish to use. (To see a list of available python versions first, type conda search "^python$" and press enter.)
conda create -n yourenvname python=x.x anaconda
Press y to proceed. This will install the Python version and all the associated anaconda packaged libraries at “path_to_your_anaconda_location/anaconda/envs/yourenvname”

- Activate your virtual environment.
To activate or switch into your virtual environment, simply type the following where yourenvname is the name you gave to your environment at creation.
source activate yourenvname
Activating a conda environment modifies the PATH and shell variables to point to the specific isolated Python setup you created. The command prompt will change to indicate which conda environment you are currently in by prepending (yourenvname). To see a list of all your environments, use the command conda info -e.

- Install additional Python packages to a virtual environment.
To install additional packages only to your virtual environment, enter the following command where yourenvname is the name of your environment, and [package] is the name of the package you wish to install. Failure to specify “-n yourenvname” will install the package to the root Python installation.
conda install -n yourenvname [package]

Otherwise install the needed libraries through the PIP Install.
Libraries list: 

Regular Expressions: pip install regex

Lxml: pip install lxml

Pyproj: pip install pyproj==1.9.6

Vtk: pip install vtk

DEPRECATED LIBRARIES -
~~Glob: pip install glob3~~
~~Os: pip install os-win~~
~~Python-Git: pip install python-git~~

(-) Deactivate your virtual environment.
To end a session in the current environment, enter the following. There is no need to specify the envname - whichever is currently active will be deactivated, and the PATH and shell variables will be returned to normal.
source deactivate

(-) Delete a no longer needed virtual environment
To delete a conda environment, enter the following, where yourenvname is the name of the environment you wish to delete.
conda remove -n yourenvname -all

____________________________________________________________________________

3 - Detailed instruction to install Ladybug + Honeybee

LADYBUG

If you have an old version of LB+HB, download the file here and open it in Grasshopper to remove your old Ladybug and Honeybee version otherwise download the latest version of Ladybug + Honeybee from Food4Rhino and follow steps below.
Make sure that you have a working copy of both Rhino and Grasshopper installed.
Open Rhino and type "Grasshopper" into the command line (without quotations). Wait for grasshopper to load.
[ONLY FOR RHINO 5] Install GHPython 0.6.0.3 by downloading the file here and drag the .gha file onto the Grasshopper canvas.
Select and drag all of the userObject files (downloaded from Food4Rhino) onto your Grasshopper canvas. You should see Ladybug and Honeybee appear as tabs on the grasshopper tool bar.
Restart Rhino and Grasshopper. You now have a fully-functioning Ladybug. For Honeybee, continue to the following:

HONEYBEE

Install Radiance to C:\Radiance by downloading it from this link and running the exe. NOTE: The default installation path for Radiance is set to C:\Program Files(x86)\Radiance which should be modified to C:\Radiance.

Install Daysim 4.0 for Windows to C:\DAYSIM by downloading it at this link and running the exe.

Install the Latest OpenStudio by downloading and running the .exe file from this link.

Install Berkeley Therm by downloading and running the .exe file from this link.

Finally, copy falsecolor2.exe to C:\Radiance\bin

You now have a fully-working version of Ladybug + Honeybee. Get started visualizing weather data with these video tutorials.



____________________________________________________________________________

4 - Download the folder with the files: 

Drive: https://drive.google.com/open?id=1SDm9r7wPmKvXGWQHFNT1yIEfxHvAOhhP

____________________________________________________________________________

5 - Open the files and adjust the paths: 

Link the environment to the ghc python: 
By clicking on the thin blue line at the bottom of any component, a new window will popup and you can choose your preferred interpreter from this window. 
Replace the local path in the main panel at the beginning of the defintion. 
Follow the instructions in the grasshopper file. 
 
____________________________________________________________________________

6 - Resources: 

https://uoa-eresearch.github.io/eresearch-cookbook/recipe/2014/11/20/conda/

https://github.com/MahmoudAbdelRahman/GH_CPython

https://github.com/mostaphaRoudsari/ladybug/wiki/Installation-Instructions



