import sys
from os.path import dirname
from iopenscad.kernel import IOpenSCAD
from ipykernel.kernelapp import IPKernelApp

## make sure that kernel is working even when we change the directory
sys.path.append(dirname(__file__))
## launch IOpenSCAD
IPKernelApp.launch_instance(kernel_class=IOpenSCAD)
