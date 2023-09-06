import os, sys
import logging
import rcdb
from rcdb.provider import RCDBProvider
from hallc_rcdb import parser
from rcdb.log_format import BraceMessage as Lf
from datetime import datetime

log = logging.getLogger("hallc.rcdb")
log.addHandler(logging.StreamHandler(sys.stdout))
log.setLevel(logging.INFO) # INFO: for less output, change it to DEBUG for printing everything

def read_startgui(fin):
    # We only need runtype and user_comment 
    parse_result = parser.runinfo_parser(fin)
    runtype = parse_result["Run"]["type"]
    comment = parse_result["comment"]['text']
    return runtype, comment

def update_DB(rnumber, rtype, rcomment):
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://rcdb@cdaqdb1.jlab.org/c-rcdb"

    # Establish db connection, check run exists
    db = rcdb.RCDBProvider(con_str)
    try:
        run = db.get_run(rnumber)
    except Exception as ex:
        log.warn("Run was not found in the database. " +  str(ex))
        # do nothing, terminate the process
        return

    # Add condiitons to update
    if rtype is not None:
        db.add_condition(run, rcdb.DefaultConditions.RUN_TYPE, rtype, True)
    if comment is not None:
        db.add_condition(run, rcdb.DefaultConditions.USER_COMMENT, comment, True)
    db.session.commit()

    # Add log
    db.add_log_record("",
                      "Update run type, user_comment: '{}'"
                      .format(datetime.now()), rnumber)


if __name__=="__main__":
    # Need two inputs, runnumber, gui output text file
    #runtype, runcomment = read_startgui(sys.argv[1], sys.argv[2])

    run_number = sys.argv[1]
    run_type = sys.argv[2]
    run_comment = sys.argv[3]
    print(run_number, run_type, run_comment)
    #update_DB(run_number, run_type, run_comment)
