import os,sys

def parse_nps_param():
   parse_result = {}
   parse_vtpconfig(parse_result)
   parse_vmeconfig(parse_result)
   print(parse_result)

def parse_vtpconfig(parse_result):
   logfile = "/home/coda/coda/scripts/EPICS_logging/Sessions/NPS/nps-vtp1.dat"
   with open(logfile, "r") as f:
      for line in [x.strip() for x in f.readlines()]:
         if "#" in line:
            if "Runnumber" in line:
               parse_result["runnumber"] = line.split(None)[2]
            elif "configtype" in line:
               parse_result["run_config"] = line.split("=")[1].strip()
            else:
               continue
         else:
            if line != "":
               name, value = line.split(None,1)
               parse_result[name] = value
   return parse_result

def parse_vmeconfig(parse_result):
   logfile = "/home/coda/coda/scripts/EPICS_logging/Sessions/NPS/nps-vme1.dat"
   with open(logfile, "r") as f:
      for line in [x.strip() for x in f.readlines()]:
         if "#" in line:
            continue
         elif "FADC250_SPARSIFICATION" in line:
            parse_result["nps_fadc250_sparsification"] = line.split(None)[1].strip()
            break
         else:
            continue
   return parse_result
