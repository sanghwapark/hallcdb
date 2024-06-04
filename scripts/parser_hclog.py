import re
import sys
import pickle
import json
import requests
from urllib import request
import os.path
import argparse

def main():

    parser = argparse.ArgumentParser(description='Helper script to check standard kinematics with epics variables. The script will read first_epics_30.results file from the logbook entry for a given run. It will dump what it reads to a dictionary and store it into a file. The run number is used as a key. If the file already exists, it will first check the file instead of accessing the logbook.')
    parser.add_argument('--runs', help='Run range', required=True)
    parser.add_argument('-m','--mode',help='Identify spectrometer: HMS, SHMS, NPS', default='NPS')
    parser.add_argument('-v','--verbose',help='Set verbose level. Default value is 0', default=0)
    args = parser.parse_args()
    
    runs = args.runs
    mode = args.mode
    verbose = args.verbose

    # For a single run test
    #dd = {}
    #get_logbook_start_run_EPICS(str(1566), dd);
    #print(dd)

    ## make run list
    ltemp = []
    for line in [x for x in runs.split(',')]:
        if '-' in line:
            brun = int(line.split('-')[0])
            erun = int(line.split('-')[1])

            for irun in range(brun, erun+1):
                ltemp.append(irun)
        else:
            ltemp.append(int(line))
            
    # remove duplicates
    lruns = list(set(ltemp))

    ## get epics variables
    dd = {}
    dd = load_epics_dict(lruns, mode)
    #print(dd['1567'])

def load_epics_dict(runs, mode):
    pickle_file = '%s.pkl' % mode

    ddict = {}

    print ("Hello, load hclog data...it may take some time")
    if os.path.isfile(pickle_file):
        infile = open(pickle_file,'rb')
        try:
            print ("We found hclog data file.....")
            ddict = pickle.load(infile)
        except EOFError:
            print ("Empty data file.. make new data file!")
        infile.close()

    for run in runs:
        run = str(run)
        if run in ddict:
            continue
        else:
            print("Get data for: ", run)
            get_logbook_start_run_EPICS(run, ddict)

    with open(pickle_file, 'wb') as ff:
        pickle.dump(ddict, ff)

    print ("HCLOG data loaded!")
    return ddict

def get_logbook_start_run_EPICS(run, ddict):
    print("Get start run data for: ", run)

    author = "cdaq"
    LOGBOOK = "HCLOG"

    prefix= 'https://logbooks.jlab.org/entry'            # Logbook entry URL prefix

    url = 'https://logbooks.jlab.org/api/elog/entries'   # Base query url
    url = url + '?book=' + LOGBOOK                       # specify Logbook
    url = url + '&limit=0'                               # return all entries

    ## Constrain date (default is -180 days. ex. look back ~6 months)
    url = url + '&startdate=2023-09-01'
    url = url + '&enddate=2024-04-30'

    ## Constrain search to a Tag
    url = url + '&tag=StartOfRun'

    ## Output fields
    url = url + '&field=attachments'
    url = url + '&field=lognumber&field=created&field=title'
    url = url + '&field=body&field=author&field=entrymakers' 
    ## Append query fields
    url = url + "&title=" + "Start_Run_" + run
    url = url + "&author=" + author

    ## One may need to put username + password
    ## if not using it from the jlab computer
    res = requests.get(url)
    res.json()
    
    dec_json = json.loads(res.text)
    #print(dec_json)

    EFILE = ['nps-vme1.dat', 'nps-vtp1.dat', 'first_epics_30.results', 'coda-flags.dat']

    if dec_json['data']['currentItems'] == 0:
        return
    else:
        #print(dec_json['data']['entries'][0]['created']['timestamp'])
        #print(dec_json['data']['entries'][0]['body']['content'])

        ddict[str(run)] = {}
        ddict[str(run)]['timestamp'] = dec_json['data']['entries'][0]['created']['timestamp']
        ddict[str(run)]['gui_content'] = dec_json['data']['entries'][0]['body']['content']

        url2 = ["","","","","",""]
        for i, item in enumerate(dec_json['data']['entries'][0]['attachments']):
            if EFILE[0] in item['url']:
                url2[0] = item['url']
            if EFILE[1] in item['url']:
                url2[1]  = item['url']
            if EFILE[2] in item['url']:
                url2[2] = item['url']
            if EFILE[3] in item['url']:
                url2[3] = item['url']

        #print(url2)

        # VME1 config file
        try:
            res2 = requests.get(url2[0])
            if res2.status_code == 200:
                ddict[str(run)]['vme1'] = {}
                parse_vmeconfig(res2, ddict[str(run)]['vme1'])
        except Exception as ex:
            print("Fail to parse vme config, ", str(ex))

        # VTP config
        try:
            res_vtp = requests.get(url2[1])
            if res_vtp.status_code == 200:
                ddict[str(run)]['vtp1'] = {}            
                parse_vtpconfig(res_vtp, ddict[str(run)]['vtp1'])
        except Exception as ex:
            print("Fail to parse vtp config, ", str(ex))

        # EPICS
        try:
            res_epics = requests.get(url2[2])
            if res_epics.status_code == 200:
                ddict[str(run)]['epics'] = {}            
                parse_epicsfile(res_epics, ddict[str(run)]['epics'])
        except Exception as ex:
            print("Fail to parse epics file, ", str(ex))

        # CODA FLAGS
        try:
            res_flags = requests.get(url2[3])
            if res_flags.status_code == 200:
                ddict[str(run)]['coda_flags'] = {}            
                parse_codaflags(res_flags, ddict[str(run)]['coda_flags'])
        except Exception as ex:
            print("Fail to parse coda flags file, ", str(ex))

def parse_codaflags(result, parse_result):
    for line in result.iter_lines():
        line = line.decode('utf8')
        if line == "":
            continue
        if ";" in line:
            continue
        if 'blocklevel' in line:
            for item in line.split(","):
                if "=" in item:
                    this_info = item.split("=")
                    parse_result[this_info[0]] = this_info[1]

def parse_epicsfile(result, parse_result):
    for line in result.iter_lines():
        line = line.decode('utf8')
        if line == "":
            continue
        if "#" in line:
            name, val_str = line.split(None,1)
            value, description = val_str.split('#',1)

            parse_result[name] = []
            parse_result[name].append(value.strip())
            parse_result[name].append(description.strip())

def parse_vmeconfig(result, parse_result):
    for line in result.iter_lines():
        line = line.decode('utf8')
        if line == "":
            continue
        if "#" in line:
            if "Runnumber" in line:
                run_num = line.split(':')[1].strip()
                parse_result['runnumber'] = run_num
            """
                if int(run) != int(run_num):
                    print("******ERROR: Run number mismatch", run, run_num)
                    sys.exit(1)
            """
            if "configtype" in line:
                config = line.split('=')[1].strip()
                parse_result['run_config'] = config
            else:
                continue
        else:
            name, value = line.split(None,1)
            parse_result[name] = value

def parse_vtpconfig(result, parse_result):
    for line in result.iter_lines():
        line = line.decode('utf8')
        if line == "":
            continue
        if "#" in line:
            continue
        name, value = line.split(None,1)
        parse_result[name] = value

def get_logbook_end_run_EPICS(run, ddict):
    print("Get end run data for: ", run)

    author = "cdaq"
    LOGBOOK = "NPS"

    prefix= 'https://logbooks.jlab.org/entry'            # Logbook entry URL prefix

    url = 'https://logbooks.jlab.org/api/elog/entries'   # Base query url
    url = url + '?book=' + LOGBOOK                       # specify Logbook
    url = url + '&limit=0'                               # return all entries

    ## Constrain date (default is -180 days. ex. look back ~6 months)
    url = url + '&startdate=2023-09-01'
    url = url + '&enddate=2024-04-30'

    ## Constrain search to a Tag
    url = url + '&tag=Autolog'

    ## Output fields
    url = url + '&field=attachments'
    url = url + '&field=lognumber&field=created&field=title'
    url = url + '&field=body&field=author&field=entrymakers' 
    ## Append query fields
    url = url + "&title=" + "NPS: End of run " + str(run)
    url = url + "&author=" + author

    ## One may need to put username + password
    ## if not using it from the jlab computer
    res = requests.get(url)
    res.json()
    
    dec_json = json.loads(res.text)
    #print(dec_json)

    EFILE = str(run) + "-NPS.log"

    if dec_json['data']['currentItems'] == 0:
        return
    else:
        #print(dec_json['data']['entries'][0]['created']['timestamp'])
        #print(dec_json['data']['entries'][0]['body']['content'])

        ddict[str(run)] = {}
        ddict[str(run)]['timestamp'] = dec_json['data']['entries'][0]['created']['timestamp']

        """
        url2 = None
        for i, item in enumerate(dec_json['data']['entries'][0]['attachments']):
            if EFILE in item:
                url2 = item['url']
                break
        print(url2)
        """
        url2 = dec_json['data']['entries'][0]['attachments'][0]['url']
        #print(url2)

        # parse the log file
        try:
            res_log = requests.get(url2)
            if res_log.status_code == 200:
                ddict[str(run)]['end_log'] = {}            
                parse_endlog(res_log, ddict[str(run)]['end_log'])
        except Exception as ex:
            print("Fail to parse end run log file, ", str(ex))

def parse_endlog(result, parse_result):

    config_name = None
    nevents = None

    for line in result.iter_lines():
        line = line.decode('utf8')
        if line == "":
            continue
        if "configtype =" in line:
            ltemp = line.split("=")[1]
            config_name = ltemp.split(",")[0]

        if "ROC1 INFO: ended after" in line:
            ltemp = line.split("(")[1]
            nevents = ltemp.split(None)[0]
    parse_result["config"] = config_name
    parse_result["nevents"] = nevents
    return

if __name__== '__main__':
    main()
