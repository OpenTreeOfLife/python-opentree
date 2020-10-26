#!/bin/bash
arg="${1}"
if test -z $arg ; then
    nosetests opentree --with-coverage --cover-branches --cover-package=opentree
else
    hd=$(dirname $0)
    rhd=$(realpath "${hd}")
    echo "rhd=${rhd}"
    if ! test -d "${arg}/testopentree" ; then
        echo "directory ${arg}/testopentree does not exist"
        exit 1
    else
        export PYTHON_OPENTREE_DIR="${rhd}"
        nosetests opentree testopentree --with-coverage --cover-branches --cover-package=opentree
    fi
fi

## To run tests in a virual environemnt and avoid conflicts with system level nose install:
## python -m nose opentree/test/
