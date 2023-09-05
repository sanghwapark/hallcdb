#!/bin/bash

RCDB_DIR=/home/cdaq/rcdb/rcdb
HCDB_DIR=/home/cdaq/rcdb/hallcdb

# RCDB environment 
if [[ -z "$RCDB_HOME" ]]; then
    export RCDB_HOME=$RCDB_DIR
fi

if [[ -z "$LD_LIBRARY_PATH" ]]; then
    export LD_LIBRARY_PATH=$RCDB_HOME/cpp/lib
else
    export LD_LIBRARY_PATH=$RCDB_HOME/cpp/lib:$LD_LIBRARY_PATH
fi

if [[ -z "$PYTHONPATH" ]]; then
    export PYTHONPATH=$RCDB_HOME/python
else
    export PYTHONPATH=$RCDB_HOME/python:$PYTHONPATH
fi

export PATH="$RCDB_HOME":"$RCDB_HOME/bin":"$RCDB_HOME/cpp/bin":$PATH

# Hall C
export PYTHONPATH="$HCDB_DIR":$PYTHONPATH


# Connection string
export RCDB_CONNECTION=mysql://rcdb@cdaqdb1.jlab.org/c-rcdb
#export RCDB_CONNECTION=mysql://rcdb@cdaqdb1.jlab.org/rcdb
