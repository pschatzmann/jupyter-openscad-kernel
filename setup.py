import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="openscad-kernel",
    version="1.0.3",
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
    install_requires=[],
    entry_points={
        "console_scripts": [
            "realpython=iopenscad.__main__:main",
        ]
    },
)
