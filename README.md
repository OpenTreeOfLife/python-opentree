python-opentree
===============
[![Build Status](https://travis-ci.org/OpenTreeOfLife/python-opentree.svg?branch=master)](https://travis-ci.org/OpenTreeOfLife/python-opentree)[![Documentation](https://readthedocs.org/projects/opentree/badge/?version=latest&style=flat)](https://opentree.readthedocs.io/en/latest/)

This package is a python library designed to make it easier to work with web services and
data resources associated with the [Open Tree of Life](https://opentreeoflife.github.io)
project.
The git repo is at https://github.com/OpenTreeOfLife/python-opentree.


Prior work / design / road map
==============================

This package will use supersede [peyotl](http://opentreeoflife.github.io/peyotl/) at
    some point.

The initial goal is provide client-side interface for an
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

