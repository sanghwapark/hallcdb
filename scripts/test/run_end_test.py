import os, sys
from datetime import datetime
import logging
import time
import argparse

import rcdb
from rcdb.provider import RCDBProvider
from rcdb.log_format import BraceMessage as Lf

from hallc_rcdb import runlog_parser as logparser
import hallc_rcdb.helper as helper

log = logging.getLogger("hallc.rcdb")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

TEST_MODE = True

def end_run_update(run_num, logfile):
    
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # for the log
    script_start_clock = time.clock()
    script_start_time = time.time()

    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://rcdb@cdaqdb1.jlab.org/c-rcdb"

    # Wait for 3 sec for the daq run-log to be written at end of run
    time.sleep(3)

    # Parse information from coda run-log
    parse_result = logparser.parse_file(logfile)

    # To be safe, parse previous log as well
    prev_log_file = logfile.split("current")[0] + "previous_run.log"
    parse_result2 = logparser.parse_file(prev_log_file)

    db = rcdb.RCDBProvider(con_str)
    run = db.get_run(run_num)
    if not db.get_run(run_num):
        log.info(Lf("run_end: Run '{}' is not found in DB.", run_num))
        return
        
    def updateDB(result, run):
        # Run end time
        if result.end_time is None:
            run.end_time = time_now
        else:
            run.end_time = datetime.strptime(result.end_time, "%m/%d/%y %H:%M:%S")        
            # Also update start time
            #run.start_time = datetime.strptime(result.start_time, "%m/%d/%y %H:%M:%S")        

        # Estimate total run time
        total_run_time = -1
        if run.start_time:
            total_run_time = (run.end_time - run.start_time).total_seconds()

        # Add conditions to update
        conditions = []
        # Total event from coda run-log
        if result.event_count is not None:
            conditions.append((rcdb.DefaultConditions.EVENT_COUNT, result.event_count))
            if total_run_time > 0:
                event_rate = float(result.event_count) / float(total_run_time)
                conditions.append((rcdb.DefaultConditions.EVENT_RATE, event_rate))

        conditions.append((rcdb.DefaultConditions.IS_VALID_RUN_END, result.has_run_end))

        # Estimate total charge based on average bean current delivered
        # Skip this now, myStats not available from coda@cdaql6
        """
        charge = 0
        avg_current = helper.get_epics_avg(run, "ibcm1", 0, 100)
        if avg_current is not None:
        charge = float(total_run_time) * float(avg_current)
        else:
        avg_current = 0 # set to 0

        #conditions.append(("beam_current", avg_current))
        #conditions.append(("total_charge", charge))
        """        

        if TEST_MODE:
            print("Run Start Time:\t %s" % run.start_time)
            print("Run End Time:\t %s" % run.end_time)
            print("Run length:\t %f" % (float(total_run_time)))
            print("Total event counts %d" % (int(result.event_count)))
            print("Event rate %.2f" % (float(event_rate)))
        else:
            db.add_conditions(run, conditions, replace=True)
            db.session.commit()

            now_clock = time.clock()
            db.add_log_record("",
                              "End of run update. Script proc clocks='{}', wall time: '{}', datetime: '{}'"
                              .format(now_clock - script_start_clock,
                                      time.time() - script_start_time,
                                      datetime.now()), run_num)

    if run_num == parse_result.run_number:
        updateDB(parse_result, run)
    elif run_num == parse_result2.run_number:
        updateDB(parse_result2, run)
    else:
        print("Run number mismatch", run_num, parse_result.run_number, parse_result2.run_number)

if __name__== "__main__":
    parser = argparse.ArgumentParser(description="Update HallC RCDB at the end of a run")
    parser.add_argument("runlog_xml_file", type=str, help="full path to coda run-log output file")
    parser.add_argument("--run", type=str, help="Run number", required=True)

    args = parser.parse_args()
    logfile = args.runlog_xml_file
    run_number = args.run
    end_run_update(run_number, logfile)
