import setuptools
from setuptools import setup

setup(
    name="forestryfunctions",
    description="Forestry functions for manipulating state of forest-data-model instances",
    version="0.12.1",
    packages=setuptools.find_namespace_packages(include=['forestryfunctions*']),
    package_data={'forestryfunctions': ['r/*']},
    dependency_links=['https://github.com/menu-hanke/forest-data-model@0.4.7#egg=forestdatamodel']
)
