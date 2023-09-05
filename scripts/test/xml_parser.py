import os,sys
import xml.etree.ElementTree as Et
from subprocess import check_output
from hallc_rcdb.parser import CodaParseResult

def xml_parser(fin, coda_parse_result):
    xml_root = Et.parse(fin).getroot()
    if xml_root.tag == 'coda':
        if "runtype" in xml_root.attrib:
            coda_parse_result.config = xml_root.attrib["runtype"]
        if "session" in xml_root.attrib:
            coda_parse_result.session_name = xml_root.attrib["session"]
        
    # run-start log
    xml_result = xml_root.find("run-start")
    if xml_result is None:
        return 

    coda_parse_result.runnumber = int(xml_root.find("run-start").find("run-number").text)
    coda_parse_result.start_time = xml_root.find("run-start").find("start-time").text
    coda_parse_result.out_file = xml_root.find("run-start").find("out-file").text
    
    # end-run log
    xml_result = xml_root.find("run-end")
    if xml_result is None:
        return
    coda_parse_result.end_time = xml_root.find("run-end").find("end-time").text
    coda_parse_result.total_evt = xml_root.find("run-end").find("total-evt").text

    return

if __name__=="__main__":

    parse_result = CodaParseResult()
    xml_parser(sys.argv[1], parse_result)
    print(parse_result.start_time, parse_result.end_time, parse_result.total_evt)
