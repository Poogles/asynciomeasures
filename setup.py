#!/usr/bin/env python3
from setuptools import setup, find_packages


setup(
    name='asynciomeasures',
    version='1.0.0',
    description="Collect and send metrics to StatsD",
    author="Sam Pegler",
    author_email='sam@sampegler.co.uk',
    url='https://github.com/Poogles/asynciomeasures',
    packages=find_packages(),
    keywords=[''],
    install_requires=[],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ],
    license='MIT'
)
