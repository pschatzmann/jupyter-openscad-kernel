from iopenscad.kernel import IOpenSCAD

if __name__ == '__main__':
    print("Starting kernel IOpenSCAD...")
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=IOpenSCAD)
