
##
# Installs the Jupyter kernel specification including the icons
#
import pathlib, os, distutils.core, setuptools 
import pkg_resources
from pathlib import Path

def main():
    kernelPath = pathlib.Path(__file__).parent / "openscad"
    if not os.path.isdir(kernelPath):
        raise Exception('The directory does not exist {}'.format(str(kernelPath)))

    if not os.path.exists(kernelPath / "kernel.json"):
        raise Exception('The kernel does not exist {}'.format(str(kernelPath)))

    cmd = 'jupyter kernelspec install ' + str(kernelPath)
    if os.system(cmd) != 0:
        raise Exception('Could not install kernelspec {}'.format(cmd))

if __name__ == "__main__":
    main()

