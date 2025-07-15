import os, sys
import json
import logging
import xml.etree.ElementTree as Et
import subprocess
from datetime import datetime

import rcdb
from rcdb.log_format import BraceMessage as Lf
from hallc_rcdb import parser
from hallc_rcdb.parser import CodaParseResult
from hallc_rcdb import runlog_parser as logparser

log = logging.getLogger("hallc.rcdb.coda")
log.addHandler(logging.NullHandler())

def get_coda_conds(session, logfile, reason):
    # parse coda info from log file
    conditions = {}

    if reason == "start":
        try:
            parse_result = CodaParseResult()
            parser.coda_parser(session, parse_result)

            if parse_result.runnumber is None:
                log.warning("ERROR: Coda parser run number mismatch.\n")

            conditions["run_number"] = parse_result.runnumber
            conditions["session"] = parse_result.session_name
            conditions["run_config"] = parse_result.config
            conditions["prescales"]  = json.dumps(parse_result.prescales)
        except Exception as ex:
            log.warning("Start run coda parser failed.\n" + str(ex))

    if reason == "end":
        parse_result = logparser.CodaRunLogParseResult()
        xml_root = Et.parse(logfile).getroot()
        try:
            logparser.parse_start_run_data(parse_result,xml_root)
            logparser.parse_end_run_data(parse_result,xml_root)
            conditions["run_number"] = parse_result.run_number
            conditions["session"]    = parse_result.session
            conditions["run_config"] = parse_result.config
            conditions["start_time"] = parse_result.start_time
            conditions["evio_file"] = parse_result.evio_file
            conditions["end_time"]   = parse_result.end_time
            conditions["event_count"] = parse_result.event_count
        except Exception as ex:
            log.warning("End run coda log parser failed.\n" + str(ex))
    return conditions

def update_db(db, run, reason, conditions):

    # Start of run update
    if reason == "start":
        # Update DB
        try:
            if "session" in conditions:
                db.add_condition(run, "session", conditions["session"], True)
            if "run_config" in conditions:
                db.add_condition(run, "run_config", conditions["run_config"], True)
            if "prescales" in conditions:
                db.add_condition(run, "prescales", conditions["prescales"], True)
            if "blocklevel" in conditions:
                db.add_condition(run, "blocklevel", conditions["blocklevel"], True)   
        except Exception as ex:
            log.warning("Update_coda: Fail to update DB.\n" + str(ex))
            db.add_log_record("", "Start of run: coda update failed", run.number)
            
    # End of run update
    if reason in ["update", "end"]:
        if int(conditions["run_number"]) != int(run.number):
            log.warning("ERROR: Coda parser run number mismatch.\n" + str(ex) )
            conditions["run_number"] = run.number
        
        # Update start time
        #if "start_time" in conditions:
        #    run.start_time = datetime.strptime(conditions["start_time"], "%m/%d/%y %H:%M:%S")

        # Run end time
        if "end_time" in conditions:
            run.end_time = datetime.strptime(conditions["end_time"], "%m/%d/%y %H:%M:%S")
        else:
            run.end_time = datetime.now()

        if run.start_time and "event_count" in conditions:
            total_time = (run.end_time - run.start_time).total_seconds()
            if total_time > 0:
                event_rate = float(conditions["event_count"]) / float(total_time)
                conditions["event_rate"] = event_rate
        # Update DB
        try:
            if "event_count" in conditions:
                db.add_condition(run, "event_count", conditions["event_count"], True)
            if "event_rate" in conditions:
                db.add_condition(run, "event_rate", conditions["event_rate"], True)

            db.add_condition(run, "is_valid_run_end", True, True)

        except Exception as ex:
            log.warning("Update_coda: Fail to update DB.\n" + str(ex))
            db.add_log_record("", "End of run: coda update failed", run.number)               

if __name__ == "__main__":
    filename = "/home/hccoda/coda/cool/COINC/ddb/run-log/RSIDIS/previous_run.log"
    result = get_coda_conds("COINC", filename, "end")
    print(result)
