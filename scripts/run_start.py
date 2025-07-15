import os, sys
import json
from datetime import datetime, timedelta
import argparse
import logging

import rcdb
from rcdb.log_format import BraceMessage as Lf
from hallc_rcdb import HallCconditions, parser
from hallc_rcdb.parser import CodaParseResult, EpicsParseResult
#from hallc_rcdb.parse_nps_param import parse_nps_param

# Define EPICS LIST
epics_list = {
    "HALLC:p":HallCconditions.BEAM_ENERGY,
    "HALL_C_TARGET":HallCconditions.TARGET,
    "ibcm1":HallCconditions.BEAM_CURRENT,
    "ecSHMS_Angle":HallCconditions.SHMS_ANGLE,
    "ecHMS_Angle":HallCconditions.HMS_ANGLE,
    "PWF1I06:spinCalc":HallCconditions.HWIEN,
    "PWF1I04:spinCalc":HallCconditions.VWIEN,
    "HELFREQ":HallCconditions.HELICITY_FREQ,
    "HMS_Momentum":HallCconditions.HMS_MOMENTUM,
    "IGL1I00OD16_16":HallCconditions.IHWP
}

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
    argparser.add_argument("--daq",  help="DAQ session: LAD, HMS, SHMS", required=True)
    argparser.add_argument("--update", help="Comma separated, modules to update such as coda, epics", default="coda,epics")
    argparser.add_argument("--reason", help="Reason for the update: start, update, end", default="start")
    argparser.add_argument("--exp", help="Experiment name", default="LAD")
    argparser.add_argument("--test", help="Test mode flag", default=False)
    argparser.add_argument("-v","--verbose", help="increase output verbosity", action="store_true")
    argparser.add_argument("-c","--connection", help="connection string, e.g: mysql://rcdb@cdaqdb1.jlab.org/c-rcdb")
    argparser.add_argument("--dist", help="Calorimeter distance", default=9.5)
    args = argparser.parse_args()

    # Set log output level
    log.setLevel(logging.DEBUG if args.verbose else logging.INFO)

    # Run number to update
    run_num = args.run

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

    # Conditions to add
    conditions = []

    # Set experiment name
    conditions.append(("experiment", args.exp))

    # What to update
    update_parts = []
    if args.update:
        update_parts = args.update.split(",")
    log.debug(Lf("update parts = '{}'", update_parts))

    # Why are we updating
    update_reason = args.reason
    log.debug(Lf("update reason = '{}'", update_reason))

    # parse epics info
    if "epics" in update_parts:
        log.debug(Lf("Adding epics info to DB", ))
        epics_result = parser.epics_parser(epics_list)

        # add conditions
        for key in epics_result:
            if epics_result[key] is not None:
                conditions.append((key, epics_result[key]))
                
    # parse coda info
    if "coda" in update_parts:
        # General daq stuff
        try:
            coda_parse_result = CodaParseResult()
            this_session = str(args.daq)
            log.debug(Lf("Adding coda conditions to DB", ))
            parser.coda_parser(this_session, coda_parse_result)

            if coda_parse_result.runnumber is None:
                log.warn("ERROR: Coda parser run number mismatch.\n")
                # use user input runnumber
                coda_parse_result.runnumber = run_num

            if int(coda_parse_result.runnumber) != int(run_num):
                run_num = int(coda_parse_result.runnumber)

            conditions.append((rcdb.DefaultConditions.SESSION, coda_parse_result.session_name))
            conditions.append((rcdb.DefaultConditions.RUN_CONFIG, coda_parse_result.config))
            conditions.append(("prescales", json.dumps(coda_parse_result.prescales)))
            #conditions.append(("blocklevel", coda_parse_result.blocklevel))

        except Exception as ex:
            log.warn("coda run log parser failed.\n" + str(ex))
            db.add_log_record("", 
                              "Start of run: coda parser failed", run_num)

    ######  UPDATE  ######
    if args.test:
        print(conditions)
    else:
        try:
            run = db.get_run(run_num)
            if not run:
                run = db.create_run(run_num)

            # Update the DB
            run.start_time = time_now
            db.add_conditions(run, conditions, replace=True)    
            db.session.commit()
            db.add_log_record("", "Start of run update", run_num)
        except Exception as ex:
            log.warn("fail to update RCDB\n" + str(ex))

def get_usage():
    return """
    
    Usage:
    python3 run_start.py --run=<run number> --session=[HMS,SHMS,LAD] -c <db_connection string> --update=[coda,epics] --reason=[start,update,end] --exp=LAD

    Examples:
    Update epics info only, at the start of run
    > python3 run_start.py --run=123 --session=HMS --update=epics --reason=start --exp=LAD

    Update both coda, epics info, at the end of the run
    > python3 run_start.py --run=123 --session=HMS --update=coda,epics --reason=end --exp=LAD

    Run the script in Test mode:
    > python3 run_start.py --test --run=123 --session=HMS --update=coda,epics --reason=end --exp=LAD
    """
    
if __name__=="__main__":
    main()
