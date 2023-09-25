import os,sys
import argparse
from datetime import datetime

import rcdb
from rcdb.provider import RCDBProvider
from hallc_rcdb import data_parser

def get_info_from_logfile(run_num, session, lruninfo):
    # Parse information from logfile

    # The runnumber used for file name and the actual run number for data are different by 1.. -_-
    # So, we correct it here: str(run_num -1)

    new_run = int(run_num) -1
    logfile = "/home/coda/debug_logs/" + session + "_logruninfo_" + str(new_run) + ".log"
    
    def read_file(fname, linfo):
        with open(fname, "r") as f:
            for line in [x.strip() for x in f.readlines()]:
                if "Keyword" in line:
                    litem = line.split(",")
                    for item in litem:
                        if "Start_Run_" in item:
                            runnumber = item.split("_Run_")[1]
                            linfo["runnumber"] = runnumber
                        else:
                            if "=" in item:
                                key = item.split("=")[0]
                                val = item.split("=")[1]
                                linfo[str(key)] = val
                    # we are done once we parse the info
                    return linfo

    try:
        read_file(logfile, lruninfo)
    except Exception as ex:
        print ("ERROR: Can't find the log file")
        return 1

    # Check if the run numbers match
    if "runnumber" not in lruninfo:
        return 2

    if int(lruninfo["runnumber"]) != int(run_num):
        print("ERROR: Run number mismatch: ", lruninfo["runnumber"], run_num)
        return 2
    return 0

def update_DB(run_num, session, forceUpdate=False):
    # Connection
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://rcdb@cdaqdb1.jlab.org/c-rcdb"

    db = RCDBProvider(con_str)
    
    run = db.get_run(run_num)
    if not run:
        print("Run doesn't exist in DB:", run_num)
        print("ERROR: Fail to update RCDB")

        if forceUpdate:
            print("Create new run in DB: ", run_num)
            run = db.create_run(run_num)
        else:
            print("If you know what you are doing, run the script with --forceUpdate\n")
            return

    # Get run info from data
    parse_result = data_parser.get_run_info_from_data(run_num)
    #if parse_result.start_time:
    #    run.start__time = parse_result.start_time
    if parse_result.end_time is not None:
        print("Parse run end time from data file")
        run.end_time = parse_result.end_time
        db.add_condition(run, rcdb.DefaultConditions.IS_VALID_RUN_END, parse_result.has_run_end, True)
    if parse_result.event_count is not None:
        db.add_condition(run, "event_count", parse_result.event_count, True)
        
    runinfo = {}
    runinfo_OK = get_info_from_logfile(run_num, session, runinfo)
    if runinfo_OK == 0:
        if runinfo["Run_type"] != "":
            db.add_condition(run, "run_type", runinfo["Run_type"])
        if runinfo["comment_text"] != "":        
            db.add_condition(run, "user_comment", runinfo["comment_text"])
    else:
        print("Can't get run info from debug_logs: ", run_num)

    print(run.start_time, run.end_time)
    try:
        db.session.commit()
        db.add_log_record("","Update with fix_rundb.py", run_num)
        print("Updated RCDB for run ", run_num)
    except Exception as ex:
        print(str(ex))

    return

if __name__=="__main__":
    argparser = argparse.ArgumentParser(description="Fix script for RCDB")
    argparser.add_argument("--run", type=str, help="Run Number to update", required=True)
    argparser.add_argument("--forceUpdate", help="Force to update if the run doesn't exist in the DB", default=False)
    argparser.add_argument("--session", help="DAQ session: NPS, HMS, SHMS", default="NPS")
    args = argparser.parse_args()
    update_DB(args.run, args.session, args.forceUpdate)
