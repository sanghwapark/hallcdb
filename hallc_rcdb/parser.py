import os, sys
import logging
import xml.etree.ElementTree as Et
from subprocess import check_output
import subprocess
from datetime import datetime

from rcdb.log_format import BraceMessage as Lf
from hallc_rcdb import HallCconditions

log = logging.getLogger("hallc.rcdb")
log.addHandler(logging.NullHandler())

class EpicsParseResult(object):
    def __init__(self):
        self.beam_energy = None        # Beam Energy
        self.target = None             # Target name
        self.target_enc = None         # Target Encoder Positions
        self.hms_angle = None          # HMS angle 
        self.shms_angle = None         # SHMS angle         
        self.nps_angle = None          # NPS angle 
        self.beam_current = None       # Beam Current
        self.hwien = None              # HWien angle
        self.vwien = None              # VWien angle
        self.helicity_freq = None      # Helicity frequency

class CodaParseResult(object):
    def __init__(self):
        self.session_name = None
        self.config = None
        self.runnumber = None
        self.out_file = None
        self.start_time = None
        self.end_time = None
        self.total_evt = None

"""
class GUIParseResult(object):
    def __init__(self):
        self.run_type = None
        self.user_comment = None
        self.target = None
"""

def epics_parser(epics_list):
    parse_result = {}
    for epics_name, cond_name in epics_list.items():
        parse_result[cond_name] = None
        try:
            cmds = ['caget', '-t', epics_name]
            out_str = subprocess.Popen(cmds, stdout=subprocess.PIPE).stdout.read().strip()
            value = out_str.decode('ascii')
            parse_result[cond_name] = float(value)
        except Exception as ex:
            log.warning("Error: " + str(ex))
            continue
    return parse_result

def coda_parser(session):

    parse_result = CodaParseResult()

    # default paths
    #runtyp_file = "/home/coda/coda/datafile/actRunType"
    #runnum_file = "/home/coda/coda/datafile/rcRunNumber"

    # control session files
    """
    Example structure:
    <control>
       <session>
          <name>HMS</name>
          <config>hms</config>
          <runnumber>1040</runnumber>
       </session>
    </control>
    """
    if session is None:
        # do something        
        return parse_result
        
    file_path = "/home/coda/coda/cool/" + session + "/ddb/controlSessions.xml"
    xml_root = Et.parse(file_path).getroot()
    xml_result = xml_root.find("session").text
    if xml_result is None:
        log.warning("No session found in controlSessions.xml")
        return parse_result
    
    parse_result.session_name = xml_root.find("session").find("name").text
    parse_result.config = xml_root.find("session").find("config").text
    parse_result.runnumber = int(xml_root.find("session").find("runnumber").text)
    
    return parse_result

def runlog_parser(logfile, coda_parse_result):
    # coda run-log xml file parser

    xml_root = Et.parse(logfile).getroot()
    if xml_root.tag == 'coda':
        if "runtype" in xml_root.attrib:
            coda_parse_result.config = xml_root.attrib["runtype"]
        if "session" in xml_root.attrib:
            coda_parse_result.session_name = xml_root.attrib["session"]
        
    # run-start log
    xml_result = xml_root.find("run-start")
    if xml_result is None:
        return

    coda_parse_result.runnumber = xml_root.find("run-start").find("run-number").text
    coda_parse_result.start_time = xml_root.find("run-start").find("start-time").text
    coda_parse_result.out_file = xml_root.find("run-start").find("out-file").text
    
    # end-run log
    xml_result = xml_root.find("run-end")
    if xml_result is None:
        return
    coda_parse_result.end_time = xml_root.find("run-end").find("end-time").text
    coda_parse_result.total_evt = xml_root.find("run-end").find("total-evt").text

def runinfo_parser(runinfo_file):
    # parse info from a run start gui output file
    runinfo = {}
    with open(runinfo_file, "r") as f:
        output = f.read()
        d_info = filter(None, [x.strip() for x in output.strip().split("[")])
        for line in d_info:
            subj = line.split("]\n",1)[0]
            runinfo[subj] = {}
            for cont in [x.strip() for x in line.split("]\n",1)[1].split("\n")]:
                group = cont.split(":",1)[0]
                var = cont.split(":",1)[1]
                runinfo[subj][group] = var

    return runinfo
