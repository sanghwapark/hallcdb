import os
import sys
import logging
import traceback
import time
from datetime import datetime
import argparse

#rcdb
import rcdb
from rcdb import RCDBProvider
from rcdb.log_format import BraceMessage as Lf

log = logging.getLogger('pvdb')
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.INFO)

TESTMODE = False

def get_usage():
    return """
    python3 update_conditions.py <input dat>

    Input file format
    <Run#> <Condition name> <new value>
    Examples:
    Updating user_comment:
    3000 user_comment this is a test

    Uptaing nps angle:
    3000 nps_angle 17.17

    Uptaing run type for run 3000-3002
    3002 run_type Cosmics
    3001 run_type Cosmics
    3000 run_type Cosmics

    To find condition list:
    hallcweb.jlab.org/rcdb/conditions/
    """

def update_conditions(input_data):

    script_start_clock = time.clock()
    script_start_time = time.time()
    last_run = None    

    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://rcdb@cdaqdb1.jlab.org:3306/c-rcdb"

    db = RCDBProvider(con_str)

    with open('%s' % input_data, 'r') as f:
        for line in f:
            #parse data
           run_num = (line.split(None,2)[0]).strip()
           condition_name = (line.split(None,2)[1]).strip()
           value = (line.split(None,2)[2]).strip()
           print(run_num, condition_name, value)

           if not run_num.isdigit():
               log.warn(Lf("ERROR: wrong format, run should be number! Your input: '{}'", run_num))
               continue

           # check db entry and update
           run = db.get_run(run_num)
           if not run:
               log.warn(Lf("Run '{}' is not found in DB.. skip this run", run_num))
               continue
           else:
               last_run = run_num
               try:
                   cnd_type = db.get_condition_type(condition_name)
                   if not TESTMODE:
                       db.add_condition(run, condition_name, value, True)
                       db.add_log_record("",
                                         "Update condition:'{}'. time: '{}'"
                                         .format(condition_name, 
                                                 datetime.now()), run_num)
                   else:
                       print (run_num, condition_name, value)
               except Exception as ex:
                   log.warn("ERROR: wrong condition name. Internal exception:\n" + str(ex))

    if not TESTMODE:
        now_clock = time.clock()
        db.add_log_record("",
                          "End of update. Script proc clocks='{}', wall time: '{}', datetime: '{}'"
                          .format(condition_name, 
                                  now_clock - script_start_clock,
                                  time.time() - script_start_time,
                                  datetime.now()), last_run)

if __name__== '__main__':

    description = "Script for updating DB conditions"
    parser = argparse.ArgumentParser(description=description, usage=get_usage())

    inputfile  = sys.argv[1]
    update_conditions(inputfile)
