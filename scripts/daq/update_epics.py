import os,sys
import logging
from epics import caget, caput
from datetime import datetime, timedelta
import subprocess
import rcdb
from rcdb.log_format import BraceMessage as Lf

log = logging.getLogger("hallc.rcdb.epics")
log.addHandler(logging.NullHandler())

########################################
# EPICS helper functions for HallC RCDB
########################################

def get_run_conds():
    log.debug("Get epics run conditions")

    # Default run conditions
    epics_list = {
        "HALLC:p":"beam_current",
        "HALL_C_TARGET":"target",
        "ibcm1":"beam_current",
        "ecSHMS_Angle":"shms_angle",
        "ecHMS_Angle":"hms_angle",
        "PWF1I06:spinCalc":"hwien",
        "PWF1I04:spinCalc":"vwien",
        "HELFREQ":"helicity_freq",
        "HMS_Momentum":"hms_momentum",
        "IGL1I00OD16_16":"ihwp"
    }
    
    conditions = {}
    for epics_name, cond_name in epics_list.items():
        conditions[cond_name] = None
        try:
            conditions[cond_name] = caget(epics_name)
        except Exception as ex:
            log.warning("Error: " + str(ex))
            continue

    return conditions

def update_conds(run, epics_name, rmin, rmax):
    conditions = {}
    # update avg run conditions at the end of the run
    start_time = datetime.strftime(run.start_time, "%Y-%m-%d %H:%M:%S")

    if run.end_time:
        end_time = datetime.strftime(run.end_time, "%Y-%m-%d %H:%M:%S")
    else:
        # Use time now instead
        now_time = datetime.now()
        end_time = now_time.strftime("%Y-%m-%d %H:%M:%S")
        
    try:
        range_str = str(rmin) + ":" + str(rmax)
        cmds = ["myStats", "-b", start_time, "-e", end_time, "-c", epics_name, "-r", range_str, "-l", epics_name]
        cond_out = subprocess.Popen(cmds, stdout=subprocess.PIPE)
        n = 0
        for line in cond_out.stdout:
            line = line.decode('ascii')
            n += 1
            if n == 1: # skip header
                continue
            tokens = line.strip().split()
            if len(tokens) < 3:
                continue
            key = tokens[0]
            value = tokens[2]
            if value == "N/A":
                value = 0
            if key == epics_name:
                #this_value = value
                conditions["beam_current"] = value
    except Exception as ex:
        log.warning("ERROR: ", str(ex))
                
    return conditions

def update_db(db, run, reason):
    # Get epics data
    conditions = {}
    if reason == "start":
        conditions.update(get_run_conds())
    if reason in ["update", "end"]:
        conditions.update(update_conds(run, "ibcm1", 0.01, 100)) # change current range as needed

    # Update database
    try:
        db.add_conditions(run, conditions, replace=True)
    except Exception as ex:
        log.warning("Fail to update DB.\n" + str(ex))

    return conditions
    
if __name__ == "__main__":
    log.setLevel(logging.DEBUG)
    parse_result = get_run_conds()
    print(parse_result)
