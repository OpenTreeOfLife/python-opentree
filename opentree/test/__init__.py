#! /usr/bin/env python3

##############################################################################
#  Adapted from: DendroPy Phylogenetic Computing Library (2010 Jeet Sukumaran
#  and Mark T. Holder)
##############################################################################

"""
opentree testing suite.
"""

import unittest
import re
import os
import logging


def get_test_file_names():
    """Get list of test file names."""
    return ['testopentree.test_about']
    path = os.path.dirname(__file__)
    default_tests = _get_test_file_names_from_dir(path, 'opentree.test.')
    TEST_PYTHON_OPENTREE_DIR = os.environ.get('TEST_PYTHON_OPENTREE_DIR')
    if TEST_PYTHON_OPENTREE_DIR and os.path.exists(TEST_PYTHON_OPENTREE_DIR):
        atd = os.path.join(TEST_PYTHON_OPENTREE_DIR, 'testopentree')
        if not os.path.isdir(atd):
            logging.warning('TEST_PYTHON_OPENTREE_DIR/testopentree at "{}" does not exist'.format(atd))
        else:
            default_tests.extend(_get_test_file_names_from_dir(atd, 'testopentree.'))
    return default_tests

def _get_test_file_names_from_dir(dirpath, pref):
    files = os.listdir(dirpath)
    t = []
    pat = re.compile(r'^test.*\.py$')
    for f in files:
        if pat.match(f):
            rp = pref + f[:-3]  # [:-3] to strip ".py"
            t.append(rp)
    return t


def get_test_suite(test_file_names=None):
    """
    Creates a unittest.TestSuite from all of the modules in
    `opentree.test`. Right now, assumes (a) no subdirectories (though
    this can easily be accommodated) and (b) every test to be run is
    sitting in a module with a file name of 'test*.py', and, conversely,
    every file with a name of 'test*.py' has test(s) to be run.
    """
    if test_file_names is None:
        test_file_names = get_test_file_names()
    tests = unittest.defaultTestLoader.loadTestsFromNames(test_file_names)
    return unittest.TestSuite(tests)


def run():
    """Runs all of the unittests"""
    runner = unittest.TextTestRunner()
    runner.run(get_test_suite())


if __name__ == "__main__":
    run()
