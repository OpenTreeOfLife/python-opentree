python-opentree
===============

This package is a python library designed to make it easier to work with web services and
data resources associated with the [Open Tree of Life](https://opentreeoflife.github.io)
project.


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

    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    python setup.py develop

