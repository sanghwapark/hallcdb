import os
import sys
import subprocess
import time
from datetime import datetime
from datetime import timedelta

# rcdb stuff
import rcdb

TEST_MODE = False

def update_simple(run_num):
    
    # Connection string
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://rcdb@localhost/c-rcdb"
    
    db = rcdb.RCDBProvider(con_str)

    # Get the start/end time
    time_end= datetime.now()
    time_start = time_end - timedelta(minutes=3)

    run = db.get_run(run_num)
    if not run:
        run = db.create_run(run_num)

    # Add conditions
    run.start_time = time_start
    run.end_time = time_end

    conditions = []
    conditions.append((rcdb.DefaultConditions.USER_COMMENT, "test db entry"))
    #conditions.append((rcdb.DefaultConditions.EVENT_COUNT, 1000))
    conditions.append((rcdb.DefaultConditions.RUN_TYPE, "TEST"))
    conditions.append(("target", "Home"))

    if TEST_MODE:
        print(conditions)
    else:
        db.add_conditions(run, conditions, replace=True)    
        db.session.commit()
        
if __name__=='__main__':
    update_simple(sys.argv[1])



