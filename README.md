# Hall C RCDB

## Setting up from scratch
1) Clone this repository
  ```
  git clone https://github.com/JeffersonLab/hallcdb
  ```
2) Download rcdb (or add it as submodule)
  ```
  git clone https://github.com/JeffersonLab/rcdb
  ```
3) Set environment variables
  For HallC: 
  ```
  > cd hallcdb
  > source setup.csh
  ```
4) Check if things are set properly. For example, type:
  ```
  > rcnd
  ```
  This should show the list of condition types. </br>
  More information on the commandline tool can be found from: https://github.com/JeffersonLab/rcdb/wiki/rcnd
  
-----------------------------

## Notes:
### Connection string:
  - For updating DB entries: Master DB should be only used when making DB entries by start/end run scripts from cdaq machines. On cdaq computers, RCDB environment is set when login, and the connection string is set to the master database.
  - Please use the read-only copy otherwise:
    ```
    setenv RCDB_CONNECTION mysql://rcdb@hallcdb.jlab.org/c-rcdb
    ```
## Useful information: 
### DB GUI for users
  #### RCDB EDIT
  rcdb_edit.py: this gui allows one to update run type, comment and flag the run.
