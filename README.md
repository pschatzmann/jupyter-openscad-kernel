# OpenSCAD Kernel for Jupyter

I was missing a Jupyter Kernel for [OpenSCAD](https://www.openscad.org/). So I took up the challenge and here is the result.  

Any regular text in a cell is added to the SCAD code buffer. This allows you to build up an OpenSCAD model in multiple steps using Jupyter cells and document the design along the way.

## Preconditions
- Python and Jupyter or Jupyterlab should be installed (e.g. with the help of pip or conada) 

- Please make sure that openscad is installed on your system (e.g. with apt install openscad) and that it can be called on the command line:

openscad -v

diplays the version. E.g. 2019.12.20

## Installation

git clone https://github.com/pschatzmann/IOpenSCAD.git
cd IOpenSCAD
jupyter kernelspec install --user iopenscad


## Optional Steps
If you want to be able to display stl files you need to install a mime renderer for Jupyter. E.g

jupyter labextension install jupyterlab-viewer-3d


Now you can launch your kernel my calling

jupyter lab

or 

jupyter workspace
