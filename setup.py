#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Setup script for threadsrecon - OSINT Tool for threads.net

This setup script allows for easy installation of threadsrecon as a Python package
with a convenient command-line interface.
"""

from setuptools import setup, find_packages
import os

# Read the README file for long description
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="threadsrecon",
    version="1.0.0",
    author="threadsrecon team",
    description="OSINT Tool for threads.net - scrape, analyze, visualize and generate reports",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/offseq/threadsrecon",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "threadsrecon=main:cli_main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.yaml", "*.yml", "*.md", "*.txt"],
    },
    keywords="osint threads instagram social-media scraping analysis security",
    project_urls={
        "Bug Reports": "https://github.com/offseq/threadsrecon/issues",
        "Source": "https://github.com/offseq/threadsrecon",
        "Documentation": "https://github.com/offseq/threadsrecon/blob/main/README.md",
    },
)