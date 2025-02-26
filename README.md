# Hall C RCDB

## Setting up from scratch
1) Clone this repository
  ```
  git clone https://github.com/JeffersonLab/hallcdb
  ```
2) Set environment variables. Modify setup.csh script as needed. You will most likely need to update the first two variables to adjust the path.
  Once it's done, 
  ```
  > cd hallcdb
  > source setup.csh
  ```
3) Check if things are set properly. For example, type:
  ```
  > rcnd
  ```
  This should show the list of condition types. </br>
  More information on the commandline tool can be found from: https://github.com/JeffersonLab/rcdb/wiki/rcnd
  
-----------------------------

## Notes:
### RCDB submodule
  - rcdb package (https://github.com/JeffersonLab/rcdb) is added as submodule with a specific tag. This release version is a rather old one, but for now keep it as it is. 
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
