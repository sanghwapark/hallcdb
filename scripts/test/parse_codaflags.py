import os,sys

def parse_codaflags(fin):
    with open(fin, "r") as f:
        for line in [ x.strip() for x in f.readlines() ]:
            if ";" in line:
                continue
            
def parse_vmelog(fin):
    RunNum = None
    config = None
    with open(fin, "r") as f:
        for line in [ x.strip() for x in f.readlines() ]:
            # check run number
            if "Runnumber" in line:
                RunNum =line.split(None)[2]
            elif "configtype" in line:
                config = line.split("=")[1]
            else:
                continue
    print(RunNum, config)
    return RunNum, config
    
if __name__=="__main__":
    #parse_codaflags(sys.argv[1])
    parse_vmelog(sys.argv[1])
