#!/bin/csh

set RCDB_DIR=/home/cdaq/rcdb/rcdb
set HCDB_DIR=/home/cdaq/rcdb/hallcdb

# RCDB environment 
if ( ! $?RCDB_HOME ) then
    setenv RCDB_HOME $RCDB_DIR
endif

if ( ! $?LD_LIBRARY_PATH ) then
    setenv LD_LIBRARY_PATH $RCDB_HOME/cpp/lib
else
    setenv LD_LIBRARY_PATH $RCDB_HOME/cpp/lib:$LD_LIBRARY_PATH
endif

if ( ! $?PYTHONPATH ) then
    setenv PYTHONPATH $RCDB_HOME/python
else
    setenv PYTHONPATH $RCDB_HOME/python:$PYTHONPATH
endif

setenv PATH "$RCDB_HOME":"$RCDB_HOME/bin":"$RCDB_HOME/cpp/bin":$PATH

# Hall C
setenv PYTHONPATH "$HCDB_DIR":$PYTHONPATH


# Connection string
setenv RCDB_CONNECTION mysql://rcdb@hallcdb.jlab.org/c-rcdb
#setenv RCDB_CONNECTION mysql://rcdb@cdaqdb1.jlab.org/rcdb
