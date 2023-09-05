import os, sys

import rcdb
from rcdb.provider import RCDBProvider
from hallc_rcdb import parser

def read_startgui(fin):
    # We only need runtype and user_comment 
    parse_result = parser.runinfo_parser(fin)
    runtype = parse_result["Run"]["type"]
    comment = parse_result["comment"]['text']
    return runtype, comment

def update_DB(run_number, fin):
    con_str = os.environ["RCDB_CONNECTION"] \
        if "RCDB_CONNECTION" in os.environ.keys() \
        else "mysql://rcdb@cdaqdb1.jlab.org/c-rcdb"

    db = rcdb.RCDBProvider(con_str)
    try:
        run = db.get_run(run_number)
        


    

if __name__=="__main__":
    read_startgui(sys.argv[1])
