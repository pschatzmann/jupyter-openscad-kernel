from ipykernel.kernelbase import Kernel
from iopenscad.kernel import IOpenSCAD

####
## Start Jupyter Kernel
##
if __name__ == '__main__':
    print("Starting kernel IOpenSCAD...")
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=IOpenSCAD)
