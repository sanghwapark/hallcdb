# SQLite database backup file of HallC RCDBs

## Availble databases:
* NPS experiment (Fall2023-Spring2024): nps.sqlite

## Using SQLite database file
### RCDB interface
When using the SQLite file instead of connecting to mysql database, replace the connection string to "sqlite:///path.to.file.db". 
For example, in a python script:
> db = rcdb.RCDBProvider("sqlite:///nps.sqlite")

### C/C++ API
Example codes to be added </br>
https://www.sqlite.org/cintro.html
