import os, sys
from datetime import datetime
import logging
import time
import argparse

import rcdb
from rcdb.provider import RCDBProvider
from rcdb.log_format import BraceMessage as Lf

from hallc_rcdb.parser import CodaParseResult, runlog_parser
import hallc_rcdb.helper as helper

log = logging.getLogger("hallc.rcdb")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.DEBUG)

TEST_MODE = False

def end_run_update(run_number, logfile):
    
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # for the log
    script_start_clock = time.clock()
    script_start_time = time.time()

    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://rcdb@cdaqdb1.jlab.org/c-rcdb"

    db = rcdb.RCDBProvider(con_str)
    run = db.get_run(run_number)
    if not db.get_run(run_number):
        log.info(Lf("run_end: Run '{}' is not found in DB.", run_number))
        return

    parse_result = CodaParseResult()
    runlog_parser(logfile, parse_result)
    if parse_result.runnumber != run_number:
        log.info(Lf("run_end: Run number mismatch in run-log file, run '{}'", run_number))
        return
        
    # Run end time
    if parse_result.end_time is None:
        run.end_time = time_now
    else: 
        run.end_time = datetime.strptime(parse_result.end_time, "%m/%d/%y %H:%M:%S")

    # Estimate total run time
    total_run_time = -1
    if run.start_time:
        total_run_time = (run.end_time - run.start_time).total_seconds()

    # Total event from coda run-log
    nevts = -1
    if parse_result.total_evt is not None:
        nevts = int(parse_result.total_evt)
        
    event_rate = -1
    if float(total_run_time) > 0:
        event_rate = float(nevts) / float(total_run_time)

    # Estimate total charge based on average bean current delivered
    charge = 0
    avg_current = helper.get_epics_avg(run, "ibcm1", 0, 100)
    if avg_current is not None:
        charge = float(total_run_time) * float(avg_current)
    else:
        avg_current = 0 # set to 0
        
    # Add conditions to update
    conditions = []
    if nevts > 0:
        conditions.append((rcdb.DefaultConditions.EVENT_COUNT, nevts))
    if event_rate > 0:
        conditions.append((rcdb.DefaultConditions.EVENT_RATE, event_rate))

    conditions.append(("beam_current", avg_current))
    conditions.append(("total_charge", charge))

    if TEST_MODE:
        print("Run Start Time:\t %s" % run.start_time)
        print("Run End Time:\t %s" % run.end_time)
        print("Run length:\t %f" % (float(total_run_time)))
        print("Total event counts %d" % (int(nevts)))
        print("Event rate %.2f" % (float(event_rate)))
        print("Avg. beam current:\t %.2f" % (float(avg_current)))
        print("Total charge:\t %.2f" % (float(charge)))
    else:
        conditions.append((rcdb.DefaultConditions.IS_VALID_RUN_END, True))

        db.add_conditions(run, conditions, replace=True)
        db.session.commit()

        now_clock = time.clock()
        db.add_log_record("",
                          "End of run update. Script proc clocks='{}', wall time: '{}', datetime: '{}'"
                          .format(now_clock - script_start_clock,
                                  time.time() - script_start_time,
                                  datetime.now()), run_number)



if __name__== "__main__":
    parser = argparse.ArgumentParser(description="Update HallC RCDB at the end of a run")
    parser.add_argument("runlog_xml_file", type=str, help="full path to coda run-log output file")
    parser.add_argument("--run", type=str, help="Run number", required=True)

    args = parser.parse_args()
    logfile = args.runlog_xml_file
    run_number = args.run
    end_run_update(run_number, logfile)
