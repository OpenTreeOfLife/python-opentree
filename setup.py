#!/usr/bin/env python
import sys
import os

# setup.py largely based on
#   http://hynek.me/articles/sharing-your-labor-of-love-pypi-quick-and-dirty/
# Also see Jeet Sukumaran's DendroPy

###############################################################################
# setuptools/distutils/etc. import and configuration
try:
    # noinspection PyPackageRequirements
    import ez_setup
    try:
        ez_setup_path = " ('" + os.path.abspath(ez_setup.__file__) + "')"
    except OSError:
        ez_setup_path = ""
    sys.stderr.write("using ez_setup%s\n" % ez_setup_path)
    ez_setup.use_setuptools()
    import setuptools
    try:
        setuptools_path = " ('" + os.path.abspath(setuptools.__file__) + "')"
    except OSError:
        setuptools_path = ""
    sys.stderr.write("using setuptools%s\n" % setuptools_path)
    from setuptools import setup, find_packages
except ImportError as e:
    sys.stderr.write("using distutils\n")
    from distutils.core import setup
    sys.stderr.write("using canned package list\n")
    PACKAGES = ['opentree',
                'opentree.test',
                ]
    EXTRA_KWARGS = {}
else:
    sys.stderr.write("searching for packages\n")
    PACKAGES = find_packages()
    EXTRA_KWARGS = dict(
        include_package_data=True,
        test_suite="opentree.test"
    )

EXTRA_KWARGS["zip_safe"] = True
ENTRY_POINTS = {}
EXTRA_KWARGS['scripts'] = []

###############################################################################
# setuptools/distuils command extensions
try:
    from setuptools import Command
except ImportError:
    sys.stderr.write("setuptools.Command could not be imported: setuptools extensions not available\n")
else:
    sys.stderr.write("setuptools command extensions are available\n")
    command_hook = "distutils.commands"
    ENTRY_POINTS[command_hook] = []

    ###########################################################################
    # coverage
    ###########################################################################
    # coverage
    try:
        from opentree.test import coverage_analysis

        if coverage_analysis.OPENTREE_COVERAGE_ANALYSIS_AVAILABLE:
            sys.stderr.write("coverage analysis available ('python setup.py coverage')\n")
            ENTRY_POINTS[command_hook].append("coverage = opentree.test.coverage_analysis:CoverageAnalysis")
        else:
            assert False
    except:
        sys.stderr.write("coverage analysis not available\n")

setup(
    name='opentree',
    version='0.0.3',  # sync with __version__ in opentree/__init__.py
    description='Library for interacting with Open Tree of Life resources',
    long_description=(open('README.md').read()),
    url='https://github.com/OpenTreeOfLife/python-opentree',
    license='BSD',
    author='Emily Jane B. McTavish and Mark T. Holder',
    py_modules=['opentree'],
    install_requires=['setuptools', 'requests>=2.18', 'DendroPy>=4.4.0'],
    download_url='https://github.com/OpenTreeOfLife/python-opentree/archive/v_0.0.3.tar.gz',
    packages=PACKAGES,
    entry_points=ENTRY_POINTS,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
    ],
    **EXTRA_KWARGS
)
