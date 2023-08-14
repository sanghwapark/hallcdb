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
  ```
  source setup.csh
  ```
4) Check if things are set properly. For example, run:
  ```
  rcnd
  ```
  This should show the list of condition types.
  
-----------------------------

## Notes:
### Connection string:
  - Master DB should be only used when making DB entries by start/end run scripts from cdaq machines.
  - Please use the read-only copy otherwise.
  ```
  setenv RCDB_CONNECTION mysql://rcdb@hallcdb.jlab.org/c-rcdb
  ```
