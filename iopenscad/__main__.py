from iopenscad.kernel import IOpenSCAD

def main():
    print("Starting kernel IOpenSCAD...")
    from ipykernel.kernelapp import IPKernelApp
    IPKernelApp.launch_instance(kernel_class=IOpenSCAD)

if __name__ == '__main__':
    main()
