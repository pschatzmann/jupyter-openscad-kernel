# OpenSCAD Kernel for Jupyter

I was missing a Jupyter Kernel for [OpenSCAD](https://www.openscad.org/). So I took up the challenge and here is the result.  

Any regular text in a cell is added to the SCAD code buffer. This allows you to build up an OpenSCAD model in multiple steps using Jupyter cells and document the design along the way.

## Preconditions
- Jupyter or Jupyterlab should have been installed
- Please make sure that openscad is installed on your system (e.g. with apt install openscad) and that it can be called on the command line:

```
openscad -v
```
diplays the version. E.g. 2019.12.20

## Installation


```
pip install git+https://github.com/pschatzmann/openscad-kernel.git

pip install openscad-kernel
python -m iopenscad.install

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
- 1.0     Initial Version
- 1.0.1   Additional syntax checking; Publish to pypi

## Further Information
- A quick [Demo Workbook](https://gist.github.com/pschatzmann/d3d043161f255be90f22dc4d19969f09)

