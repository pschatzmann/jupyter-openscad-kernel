import pathlib, os, distutils.core, setuptools 
from setuptools import setup
from setuptools.command import easy_install
from setuptools.command.install import install
 

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# Extended install which also installs the kernel
class InstallKernel(install):
    def run(self):
        install.run(self)
        self.installKernel()

    def installKernel(self):
        os.system('jupyter kernelspec install openscad')
        stream = os.popen('echo Returned output')
        output = stream.read()
        output

# This call to setup() does all the work
setup(
    name="jupyter-openscad-kernel",
    version="1.0.1",
    description="Jupyter kernel for OpenSCAD",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/pschatzmann/openscad-kernel",
    author="Phil Schatzmann",
    author_email="phil.schatzmann@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["iopenscad"],
    include_package_data=True,
    install_requires=["jupyter"],
    cmdclass={'install': InstallKernel}

)



