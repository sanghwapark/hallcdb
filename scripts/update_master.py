import sys
import json
import pickle
import argparse
from datetime import datetime

# HCLOG parser
from parser_hclog import get_logbook_end_run_EPICS, get_logbook_start_run_EPICS

# RCDB
from rcdb import RCDBProvider

nps_angle_offset = 16.27
epics_list = {
    "HALLC:p":"beam_energy",
    "ibcm1":"beam_current",
    "ecSHMS_Angle":"shms_angle",
    "ecHMS_Angle":"hms_angle",
    "PWF1I06:spinCalc":"hwien",
    "PWF1I04:spinCalc":"vwien",
    "IGL1I00OD16_16":"ihwp",
    "HELFREQ":"helicity_freq",
    "HMS_Momentum":"hms_momentum",
    "MNPSSWEEP":"nps_sweeper",
    "IGL1I00OD16_16":"ihwp"
}                             

def main():
    parser = argparse.ArgumentParser(description="Post update master script for HallC RCDB")
    parser.add_argument('--runs', help="Run range", required=True)
    parser.add_argument('--test', help="Test mode", default=False) 

    args = parser.parse_args()
    runs = args.runs
    TEST_MODE = args.test

    ## Make run list 
    lrun = [] 
    for irun in runs.split(','):
        if "-" in runs:
            brun = int(runs.split('-')[0])
            erun = int(runs.split('-')[1]) 
            for this_run in range(brun, erun+1):
                lrun.append(str(this_run))
        else:
            lrun.append(irun) 

    ## Load HCLOG pickle file 
    infile1 = open('NPS.pkl', 'rb') 
    ddict1 = pickle.load(infile1)
    infile1.close()

    ## Load End Run Log Pickle file
    infile2 = open('NPS_endlog.pkl', 'rb')
    ddict2 = pickle.load(infile2)
    infile2.close()

    ## DB Connection
    if not TEST_MODE:
        con_str = "mysql://rcdb@cdaqdb1.jlab.org/c-rcdb"
        db = RCDBProvider(con_str)

    ## Loop over the runs 
    for run_num in lrun: 
        parse_result = {}

        ## Parse startrun log
        if run_num in ddict1:
            try:
                # parse info
                parse_startrunlog(ddict1[run_num], parse_result)
            except Exception as ex:
                print("Fail to parse start of run hclog information from pickle file. ", str(ex)) 
                #print("Skip this update\n")
                #continue
        else:
            try:
                ## Update pickle file
                get_logbook_start_run_EPICS(run_num, ddict1)

                # let's try again
                parse_startrunlog(ddict1[run_num], parse_result)
            except Exception as ex:
                print("Something went wrong with hclog parsing..", str(ex))
                print("Likely won't have start run log info\n")

        ## Parseendrun log
        if run_num in ddict2:
            try:
                parse_endrunlog(ddict2[run_num], parse_result)
            except Exception as ex:
                print("Fail to parse end of run hclog information from pickle file. ", str(ex))
        else:
            ## Update pickle file
            try:
                get_logbook_end_run_EPICS(run_num, ddict2)

                # try again
                parse_endrunlog(ddict2[run_num], parse_result)
            except Exception as ex:
                print("Something went wrong with hclog parsing..", str(ex))
                print("Likely won't have end run log info\n")

        if TEST_MODE:
            print(parse_result)
        else:
            run = db.get_run(run_num)
            if not run:
                run = db.create_run(run_num)
            update_run(db, run, parse_result)

    #Update pickle files
    with open('NPS.pkl', 'wb') as ff:
        pickle.dump(ddict1, ff)
    with open('NPS_endlog.pkl', 'wb') as ff:
        pickle.dump(ddict2, ff)

                
def update_run(db, run, parse_result):
    # start time
    if run.start_time is None and 'start_time' in parse_result:
        try:
            timestamp = int(parse_result['start_time'])
            run.start_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") 
        except Exception as ex:
            print("startime:", str(ex))

    # end time
    if run.end_time is None and 'end_time' in parse_result:
        try:
            timestamp = int(parse_result['end_time'])
            run.end_time = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S") 
        except Exception as ex:
            print("endtime:", str(ex))

    # Run type
    if "run_type" in parse_result and parse_result['run_type'] is not None: 
        try:
            db.add_condition(run, "run_type", parse_result['run_type'], False)
        except Exception as ex:
            print("run_type:", str(ex))

    # blocklevel
    if "blocklevel" in parse_result and parse_result["blocklevel"] is not None:
        try:
            db.add_condition( run, "blocklevel", parse_result['blocklevel'], False )
        except Exception as ex:
            print("blocklevel:", str(ex))

    # prescales
    if "prescales" in parse_result:
        try:
            db.add_condition( run, "prescales", json.dumps(parse_result["prescales"]), False )
        except Exception as ex:
            print("prescales:", str(ex))

    # DAQ run config
    if "run_config" in parse_result and parse_result['run_config'] is not None:  
        db.add_condition(run, "run_config", parse_result['run_config'], True)

    # NPS VTP config
    if "nps_vtp_clus_trigger_thr" in parse_result and parse_result['nps_vtp_clus_trigger_thr'] is not None:
        try:
            db.add_condition(run, "nps_vtp_clus_trigger_thr", parse_result['nps_vtp_clus_trigger_thr'], True)
        except Exception as ex:
            print("vtp config:", str(ex))

    if "nps_vtp_clus_readout_thr" in parse_result and parse_result['nps_vtp_clus_readout_thr'] is not None:
        try:
            db.add_condition(run, "nps_vtp_clus_readout_thr", parse_result['nps_vtp_clus_readout_thr'], True)
        except Exception as ex:
            print("vtp config:", str(ex))

    if "nps_vtp_pair_trigger_thr" in parse_result and parse_result['nps_vtp_pair_trigger_thr'] is not None:
        try:
            db.add_condition(run, "nps_vtp_pair_trigger_thr", parse_result['nps_vtp_pair_trigger_thr'], True)
        except Exception as ex:
            print("vtp config:", str(ex))

    # FADC sparsification
    if 'nps_fadc250_sparsification' in parse_result['nps_fadc250_sparsification'] and  parse_result['nps_fadc250_sparsification'] is not None: 
        try:
            db.add_condition(run, "nps_fadc250_sparsification", parse_result["nps_fadc250_sparsification"], True)
        except Exception as ex:
            print("FADC250 sparsification:", str(ex))

    # User comment
    if "user_comment" in parse_result and parse_result['user_comment'] is not None: 
        try:
            # Replace is set to False so that we don't override the already corrected comments
            db.add_condition(run, "user_comment", parse_result["user_comment"], replace=False)
        except Exception as ex:
            print("user_comment:", str(ex))

    # NPS calo distance
    """
    try:
        db.add_condition(run, "calo_distance", calo_distance, True) 
    except Exception as ex: 
        print(str(ex))
    """

    # EPICS
    for epics_name, cond_name in epics_list.items():
        if cond_name in parse_result and parse_result[cond_name] is not None:  
            if "hms_momentum" in cond_name:
                db.add_condition(run, cond_name, parse_result[cond_name], True)
            else:
                try:
                    db.add_condition(run, cond_name, parse_result[cond_name], False) 
                except Exception as ex:
                    print("epics:", str(ex))
                    
    # nevents
    if "nevents" in parse_result and parse_result['nevents'] is not None:
        try:
            db.add_condition(run, 'event_count', parse_result['nevents'], False)
        except Exception as ex:
            print("nevents:", str(ex))

def parse_endrunlog(dd, parse_result):
    # endtime (approx)
    if 'timestamp' in dd:
        parse_result['end_time'] = dd['timestamp']
    
    # nevents 
    if 'end_log' in dd:
        parse_result['nevents'] = dd['end_log']['nevents']
    
def parse_startrunlog(dd, parse_result):
    # start time (approx)
    if 'timestamp' in dd:
        parse_result['start_time'] = dd['timestamp']

    # nps-vme1.dat
    if 'vme1' in dd:
        parse_result['nps_fadc250_sparsification'] = dd['vme1']['FADC250_SPARSIFICATION']
        parse_result['run_config'] = dd['vme1']['run_config']

    # nps-vtp1.dat
    if 'vtp1' in dd:
        parse_result['nps_vtp_clus_trigger_thr'] = dd['vtp1']['VTP_NPS_ECALCLUSTER_CLUSTER_TRIGGER_THR']
        parse_result['nps_vtp_clus_readout_thr'] = dd['vtp1']['VTP_NPS_ECALCLUSTER_CLUSTER_READOUT_THR']
        parse_result['nps_vtp_pair_trigger_thr'] = dd['vtp1']['VTP_NPS_ECALCLUSTER_CLUSTER_PAIR_TRIGGER_THR']
        
    # GUI
    if 'gui_content' in dd:
        for item in [x.strip() for x in dd['gui_content'].split('<br>')][:-1]:
            if "Run_type" in item: 
                parse_result['run_type'] = item.split('=')[1]  
            if 'coda_ps' in item:
                parse_result['prescales'] = item.split('=',1)[1]
            if 'comment_text' in item:
                parse_result['user_comment'] = item.split('=',1)[1]

    # EPICS 
    if 'epics' in dd:
        for epics_name, cond_name in epics_list.items():
            parse_result[cond_name] = None
            value = dd['epics'][epics_name][0]
            if '**' in value:
                # not connected
                continue
            else:
                parse_result[cond_name] = value

    # NPS angle
    if parse_result['shms_angle'] is not None: 
        parse_result['nps_angle'] = float(parse_result['shms_angle']) - nps_angle_offset

    # CODA flags
    if "coda_flags" in dd:
        ## prescale
        parse_result["prescales"] = {}  
        for ps in ["ps1", "ps2", "ps3", "ps4", "ps5", "ps6"]:
            parse_result["prescales"][ps] = int(dd["coda_flags"][ps]) 

        ## blocklevel
        if "blocklevel" in dd["coda_flags"]:  
            parse_result["blocklevel"] = int(dd["coda_flags"]["blocklevel"]) 

    
if __name__=="__main__":
    main()


