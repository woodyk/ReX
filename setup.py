#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# File: setup.py
# Author: Wadih Khairallah
# Description: 
# Created: 2024-12-03 11:45:21
# Modified: 2024-12-03 12:02:07

from setuptools import setup, find_packages
from pkg_resources import parse_requirements

# Parse requirements from requirements.txt
with open("requirements.txt") as f:
    requirements = [str(req) for req in parse_requirements(f.read())]

setup(
    name="rex",
    version="1.0.0",
    author="Wadih Khairallah",
    author_email="woodyk@gmail.com",
    description="A powerful and flexible regex wrapper tool for Python",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/woodyk/rex",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.7",
    install_requires=requirements,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Development Status :: 5 - Production/Stable",
    ],
    keywords="regex re wrapper patterns search replace validation",
    project_urls={
        "Source": "https://github.com/woodyk/rex",
        "Tracker": "https://github.com/woodyk/rex/issues",
    },
)

