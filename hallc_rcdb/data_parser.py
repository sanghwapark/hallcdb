import os,sys                                                                                 
import xml.etree.ElementTree as Et                                                            
from subprocess import check_output                                                           
from datetime import datetime                                                                 
from glob import glob                                                                         
import shutil                                                                                 

class CodaDataParseResult(object):
    
    def __init__(self):
        self.run_number = None
        self.has_run_end = False
        self.start_time = None
        self.end_time = None
        self.event_count = None
        self.last_mod_time = None
        self.evio_files = []
                                                                                              
def get_run_info_from_data(run_number):                                                       
    # Get run start time, end time, total events                                              
    # event tag 65489 (prestart) 65490 (start?) 65492 (end)                                   
                                                                                              
    parse_result = CodaDataParseResult()
    parse_result.run_number = run_number

    # Set env to use evio2xml                                                                 
    if shutil.which("evio2xml") is None:                                                      
        path = os.environ.get("PATH")                                                         
        os.environ["PATH"] = path + ":/home/coda/coda/3.10_devel/Linux-x86_64/bin"            
                                                                                              
        libpath = os.environ.get("LD_LIBRARY_PATH")                                           
        os.environ["LD_LIBRARY_PATH"] = path + ":/home/coda/coda/3.10_devel/Linux-x86_64/lib" 
                                                                                              
    # data paths                                                                               
    data_paths = ["/home/coda/data/raw",                                                      
                  "/cache/hallc/c-nps/raw"]                                                   

    # get the list of evio files
    fname_str = "/nps*_" + str(run_number) + ".dat*"                                          
    num_files = 0                                                                             
    for data_path in data_paths:                                                              
        num_files = len([files for files in glob(data_path + fname_str)])                     
        if num_files > 0:                                                                     
            parse_result.evio_files = [files for files in glob(data_path + fname_str)]
            break                                                                             
                                                                                              
    if num_files < 1:                                                                         
        print("No data file found for ", run_number)                                          
        return parse_result
        
    # start_time                                                                              
    coda_file = parse_result.evio_files[0]
    parse_result.start_time = get_start_time_from_data(coda_file)
                                                                                              
    # end time                                                                                
    coda_file = parse_result.evio_files[-1]
    parse_result.last_mod_time = get_last_modified_time(coda_file)                                          
    end_time, nevents = get_end_time_from_data(coda_file)                                     

    if end_time is None:                                                                      
        # Use last modified time instead                                                      
        parse_result.end_time = parse_result.last_mod_time
    else:
        parse_result.has_run_end = True
        parse_result.end_time = end_time
        parse_result.event_count = nevents

    return parse_result

def get_time_from_data(coda_file, evt_tag):                                                   
    this_time = None                                                                          
    cmds = ["evio2xml", "-ev", evt_tag, "-xtod", "-max", "1", coda_file]                      
    out = check_output(cmds)                                                                  
    xml_root = Et.ElementTree(Et.fromstring(out)).getroot()                                   
    xml_check = xml_root.find("event")                                                        
    if xml_check is None:                                                                     
        return this_time                                                                      
    else:                                                                                     
        for xml_result in xml_root.findall("event"):                                          
            time_data = int(xml_result.text.split(None)[0])                                   
            this_time = datetime.fromtimestamp(time_data).strftime("%Y-%m-%d %H:%M:%S")       
            if evt_tag == "65492":                                                            
                ev_count = int(xml_result.text.split(None)[2])                                
                return this_time, ev_count                                                    
            else:                                                                             
                return this_time                                                              
                                          

def get_start_time_from_data(coda_file):                                                      
    start_time = get_time_from_data(coda_file, "65489")                                       
    return start_time                                                                         
                                                                                              
def get_end_time_from_data(coda_file):                                                        
    end_time = get_time_from_data(coda_file, "65492")                                         
    return end_time                                                                           
                                                                                              
def get_last_modified_time(coda_file):                                                        
    last_mod_time = None                                                                      
    try:                                                                                      
        mtime = os.path.getmtime(coda_file)                                                   
        last_mod_time = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M:%S")           
    except Exception as ex:                                                                   
        print ("Unable to get last modified time for the coda file: " + str(ex))              
                                                                                              
    return last_mod_time
