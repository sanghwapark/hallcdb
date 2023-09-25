# Coda run-log parser based on rcdb/coda_parser.py
# Read coda run-log file /home/coda/coda/cool/NPS/ddb/run-log
# return: CodaRunLogParseResult

import os, sys
import logging
import xml.etree.ElementTree as Et
from subprocess import check_output
import subprocess
from datetime import datetime

from rcdb.log_format import BraceMessage as Lf
from hallc_rcdb import HallCconditions

#log = logging.getLogger("hallc.rcdb")
#log.addHandler(logging.NullHandler())

# run number, session, config in rtvs 
RUN_NUM_RTV = "%(rn)"
RUN_SESSION_RTV = "%(session)"
RUN_CONFIG_RTV = "%(rt)"

class CodaRunLogParseResult(object):
    def __init__(self):
        self.run_number = None
        self.session = None
        self.config = None
        self.start_time = None
        self.end_time = None
        self.update_time = None
        self.event_count = None
        self.evio_file = None
        self.has_run_end = False

        self.components = None
        self.rtvs = None
        self.component_stats = None

def parse_file(filename):
    result = CodaRunLogParseResult()

    xml_root = Et.parse(filename).getroot()

    # Start run data
    parse_start_run_data(result, xml_root)

    # End run data
    parse_end_run_data(result, xml_root)

    return result

def parse_start_run_data(parse_result, xml_root):
    if xml_root.tag == "coda":
        if "runtype" in xml_root.attrib:
            parse_result.config = xml_root.attrib["runtype"]
        if "session" in xml_root.attrib:
            parse_result.session = xml_root.attrib["session"]

    xml_result = xml_root.find("run-start")
    if xml_result is None:
        return parse_result
    
    parse_result.run_number = xml_root.find("run-start").find("run-number").text
    parse_result.start_time = xml_root.find("run-start").find("start-time").text
    parse_result.evio_file = xml_root.find("run-start").find("out-file").text

    # parse components
    xml_components = xml_result.find("components")
    parse_components(parse_result, xml_components)

    # rtvs
    xml_rtvs = xml_result.find('rtvs')
    if xml_rtvs is not None:
        rtvs = {rtv.attrib['name']: rtv.attrib['value'] for rtv in xml_rtvs.findall('rtv')}
        parse_result.rtvs = rtvs

        """
        if RUN_CONFIG_RTV in rtvs.keys():
            parse_result.config_file = rtvs[RUN_CONFIG_RTV]
            parse_result.config = os.path.basename(parse_result.config_file)
        """
    # Update time
    parse_result.end_time = xml_result.find("update-time").text

    # Event count
    parse_result.event_count = xml_result.find("total-evt").text

def parse_end_run_data(parse_result, xml_root):
    xml_result = xml_root.find("run-end")
    if xml_result is None:
        return parse_result

    # End time
    parse_result.end_time = xml_result.find("end-time").text
    parse_result.has_run_end = True

    # Event count
    parse_result.event_count = xml_result.find("total-evt").text
    
    # parse components
    xml_components = xml_result.find("components")
    parse_components(parse_result, xml_components)

def parse_components(parse_result, xml_components):
    if xml_components is not None:
        components = {}
        components_stats = {}
        for xml_component in xml_components.findall('component'):
            stats = {}

            def find_stat(name, cast):
                xml_field = xml_component.find(name)
                if xml_field is not None:
                    stats[name] = cast(xml_field.text)

            find_stat("evt-rate", float) 
            find_stat("data-rate", float)
            find_stat("evt-number", int)
            find_stat("min-evt-size", float)
            find_stat("max-evt-size", float)
            find_stat("average-evt-size", float)

            component_type = xml_component.attrib['type']
            components[xml_component.attrib['name']] = component_type
            components_stats[xml_component.attrib['name']] = stats
            
        parse_result.components = components
        parse_result.component_stats = components_stats

    return parse_result
