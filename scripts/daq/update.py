import os, sys
import json
from datetime import datetime, timedelta
import argparse
import logging

import rcdb
from rcdb.log_format import BraceMessage as Lf
from hallc_rcdb import HallCconditions, parser
from hallc_rcdb.parser import CodaParseResult
from hallc_rcdb.parse_nps_param import parse_nps_param
#from hallc_rcdb import update_epics
#from hallc_rcdb import update_coda
import update_epics
import update_coda

def main():
    # Get the start/end time
    time_now= datetime.now()

    # logger
    log = logging.getLogger("hallc db") # create run configuration standard logger
    log.addHandler(logging.StreamHandler(sys.stdout)) # add console output for logger
    log.setLevel(logging.INFO) # INFO: for less output, change it to DEBUG for printing everything

    # parse args
    argparser = argparse.ArgumentParser(description=" Update Hall C RCDB", usage=get_usage())
    argparser.add_argument("--run", type=int, help="Run number to update", required=True)
    argparser.add_argument("--daq",  help="DAQ session: HMS, SHMS, NPS, LAD", required=True)
    argparser.add_argument("--update", help="Comma separated, modules to update such as coda, epics", default="coda,epics")
    argparser.add_argument("--reason", help="Reason for the update: start, update, end", default="start")
    argparser.add_argument("--exp", help="Experiment name", default="NPS")
    argparser.add_argument("--test", help="Test mode flag", default=False)
    argparser.add_argument("-v","--verbose", help="increase output verbosity", action="store_true")
    argparser.add_argument("-c","--connection", help="connection string, e.g: mysql://rcdb@cdaqdb1.jlab.org/c-rcdb")
    argparser.add_argument("--logfile", type=str, help="full path to coda run-log file") # optional for start update
    argparser.add_argument("--dist", help="Calorimeter distance", default=9.5)
    args = argparser.parse_args()

    # Set log output level
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # Run number to update
    run_num = args.run

    # experiment name
    experiment = args.exp

    # coda run log file
    this_session = str(args.daq)
    if args.logfile:
        logfile = args.logfile
    else:
        logfile = "/home/hccoda/coda/cool/" + this_session + "/ddb/run-log/" + experiment + "/current_run.log"

    # Connection string
    if args.connection:
        con_str = args.connection
    elif "RCDB_CONNECTION" in os.environ:
        con_str = os.environ["RCDB_CONNECTION"]
    else:
        print("ERROR: RCDB_CONNECTION is not set and is not given as a script parameter (-c)")
        argparser.print_help()
        sys.exit(2)

    # Connect to the DB
    db = rcdb.RCDBProvider(con_str)

    # What to update
    update_parts = []
    if args.update:
        update_parts = args.update.split(",")
    log.debug(Lf("update parts = '{}'", update_parts))

    # Why are we updating
    update_reason = args.reason
    log.debug(Lf("update reason = '{}'", update_reason))

    ######  UPDATE  ######
    if args.test:
        coda_conditions = {}
        coda_conditions = update_coda.get_coda_conds(this_session, logfile, update_reason)
        for cname in coda_conditions:
            print(cname, coda_conditions[cname])

        epics_conditions = update_epics.get_run_conds()
        for cname in epics_conditions:
            print(cname, epics_conditions[cname])
    else:
        try:
            run = db.get_run(run_num)
            if not run:
                run = db.create_run(run_num)
                
            if update_reason == "start":
                run.start_time = time_now
                
            # Update experiment name
            db.add_condition(run, "experiment", experiment, True)
            
            # Update coda run conds
            if "coda" in update_parts:
                log.debug(Lf("Adding coda conditions to DB", ))
                conditions = {}
                conditions = update_coda.get_coda_conds(this_session, logfile, update_reason)
                #print(conditions)
                update_coda.update_db(db, run, update_reason, conditions)

            # Update epics run conds
            if "epics" in update_parts:
                log.debug(Lf("Adding epics info to DB", ))
                update_epics.update_db(db, run, update_reason)

            db.add_log_record("", "'{}': '{}' of run update".format("update.py", update_reason), run_num)
        except Exception as ex:
            log.warnig("Fail to update RCDB\n" + str(ex))
            db.add_log_record("", "'{}': {}' of run: update failed".format("update.py", update_reason), run_num)

def get_usage():
    return """
    
    Usage:
    python3 run_start.py --run=<run number> --session=[HMS,SHMS,NPS,LAD] -c <db_connection string> --update=[coda,epics] --reason=[start,update,end] --exp=NPS

    Examples:
    Update epics info only, at the start of run
    > python3 run_start.py --run=123 --session=HMS --update=epics --reason=start --exp=NPS

    Update both coda, epics info, at the end of the run
    > python3 run_start.py --run=123 --session=HMS --update=coda,epics --reason=end --exp=NPS

    Run the script in Test mode:
    > python3 run_start.py --test --run=123 --session=HMS --update=coda,epics --reason=end --exp=NPS
    """
    
if __name__=="__main__":
    main()
