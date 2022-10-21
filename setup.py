import os

from setuptools import find_packages, setup


# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(
    name="bmodbus",
    version="0.0.1",
    author="Rubalo",
    author_email="rubalo",
    description="Reading and writing modbus registers with a batch functionnality ",
    license="BSD",
    keywords="modbus batch",
    url="https://github.com/rubalo/modbus",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    long_description=read("README.md"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=["click", "dataclasses-json", "pymodbus", "pyserial-asyncio"],
    entry_points={"console_scripts": ["bmodbus=bmodbus.main:cli"]},
    package_data={"": ["*.csv"]},
)
