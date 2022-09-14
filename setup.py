import setuptools
from setuptools import setup

setup(
    name="forestryfunctions",
    description="Forestry functions for manipulating state of forest-data-model instances",
    version="0.4.0",
    packages=setuptools.find_namespace_packages(include=['forestryfunctions*']),
    dependency_links=['https://github.com/menu-hanke/forest-data-model@0.4.1#egg=forestdatamodel']
)
