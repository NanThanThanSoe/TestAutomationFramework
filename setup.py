#setup.py is the build script for setuptools. 
#It tells setuptools about your package (such as the name and version) 
#as well as which code files to include.

import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="nantestfw",
    version="0.0.1",
    author="Nan",
    author_email="thanthansoe1994@gmail.com",
    description="Nan's thesis works",
    packages=setuptools.find_packages()
)
