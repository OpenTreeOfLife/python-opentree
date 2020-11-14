python-opentree
===============
[![Build Status](https://travis-ci.org/OpenTreeOfLife/python-opentree.svg?branch=master)](https://travis-ci.org/OpenTreeOfLife/python-opentree) [![Documentation](https://readthedocs.org/projects/opentree/badge/?version=latest&style=flat)](https://opentree.readthedocs.io/en/latest/) [![codecov](https://codecov.io/gh/OpenTreeOfLife/python-opentree/branch/main/graph/badge.svg)](https://codecov.io/gh/OpenTreeOfLife/python-opentree) [![NSF-1759846](https://img.shields.io/badge/NSF-1759846-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1759846) [![NSF-1759838](https://img.shields.io/badge/NSF-1759838-blue.svg)](https://nsf.gov/awardsearch/showAward?AWD_ID=1759838)

This package is a python library designed to make it easier to work with web services and
data resources from the [Open Tree of Life](https://opentreeoflife.github.io)
project.
The git repo is at https://github.com/OpenTreeOfLife/python-opentree.


Prior work / design / road map
==============================

This package will supersede [peyotl](http://opentreeoflife.github.io/peyotl/) at
    some point.

The initial goal is to provide client-side interface for an
[Open Tree workshop](https://opentreeoflife.github.io/SSBworkshop)
at the [2020 SSB Meeting](https://systbiol.github.io/ssb2020/) in Gainesville, FL.


Installation
============
If you don't need the latest version you, can simply use:

    pip install opentree


If you are developer who wants to install multiple times, you probably want to use:

    git clone https://github.com/OpenTreeOfLife/python-opentree.git
    cd python-opentree

to get a local copy of the code, then:

    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    python setup.py develop

Examples
========

The folder docs/notebooks contains Jupyter notebooks examples of the usage of the `python-opentree` library.

To run them locally you have to:
