import setuptools
from setuptools import setup

setup(
    name="lukefi.metsi.forestry",
    description="Forestry functions for manipulating state of metsi-data model instances",
    version="1.0.0-rc3",
    packages=setuptools.find_namespace_packages(include=['lukefi.metsi.forestry*']),
    package_data={'lukefi.metsi.forestry': ['r/*', 'lua/*']},
    dependency_links=['https://github.com/lukefi/metsi_data@1.0.0'],
    install_requires=[
        "scipy==1.7.*"
    ]
)
