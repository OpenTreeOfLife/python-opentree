#!/bin/bash
arg="${1}"
if test -z $arg ; then
    nose2 opentree --coverage opentree
else
    hd=$(dirname $0)
    rhd=$(realpath "${hd}")
    echo "rhd=${rhd}"
    if ! test -d "${arg}/opentree" ; then
        echo "directory ${arg}/opentree does not exist"
        exit 1
    else
        shift
        export PYTHON_OPENTREE_DIR="${rhd}"
        nose2 opentree testopentree opentree --coverage opentree $@
    fi
fi

## To run tests in a virual environemnt and avoid conflicts with system level nose install:
## python -m nose opentree/test/
