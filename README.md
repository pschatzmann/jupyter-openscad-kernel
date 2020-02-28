# OpenSCAD Kernel for Jupyter

I was missing a Jupyter Kernel for (OpenSCAD)[https://www.openscad.org/]. So I took up the challenge and here is the result.  

Any regular text in a cell is added to the SCAD code buffer. This allows you to build up an OpenSCAD model in multiple steps using Jupyter cells and document the design along the way.

Further documentation can be found at https://www.pschatzmann.ch/home/2020/02/26/an-openscad-kernel-in-jupyter/

## Preconditions
- Python and Jupyter or Jupyterlab should be installed (e.g. with the help of pip or conada) 

- Please make sure that openscad is installed on your system (e.g. with apt install openscad) and that it can be called on the command line:

```
openscad -v
```
diplays the version. E.g. 2019.12.20

## Installation
```
pip install openscad-kernel
```
## Installation from source
```
git clone https://github.com/pschatzmann/openscad-kernel.git
cd openscad-kernel
jupyter kernelspec install --user iopenscad
```

## Optional Steps
If you want to be able to display stl files you need to install a mime renderer for Jupyter. E.g
```
jupyter labextension install jupyterlab-viewer-3d
```
If you want to have syntax highlighting for OpenSCAD:
```
jupyter labextension install jupyterlab-openscad-syntax-highlighting
```


Now you can launch your kernel my calling
```
jupyter lab
```
or 
```
jupyter workspace
```
## Versions
1.0     Initial Version
1.0.1   Additional syntax checking
        Publish to pypi