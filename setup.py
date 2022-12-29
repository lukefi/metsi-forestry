import setuptools
from setuptools import setup

setup(
    name="forestryfunctions",
    description="Forestry functions for manipulating state of forest-data-model instances",
    version="1.0.0-rc2",
    packages=setuptools.find_namespace_packages(include=['forestryfunctions*']),
    package_data={'forestryfunctions': ['r/*']},
    dependency_links=['https://github.com/menu-hanke/forest-data-model@1.0.0-rc1#egg=forestdatamodel'],
    install_requires=[
        "scipy==1.7.*"
    ]
)
