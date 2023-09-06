import os, sys
import rcdb
import hallc_rcdb

if __name__=="__main__":

    # Connection
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://rcdb@localhost/c-rcdb"

    db = rcdb.RCDBProvider(con_str, check_version=False)

    # Delete existing db schema 
    rcdb.provider.destroy_all_create_schema(db)

    print("Create default condition types")
    rcdb.create_condition_types(db)

    print("Create Hall C condition types")
    hallc_rcdb.create_condition_types(db)
