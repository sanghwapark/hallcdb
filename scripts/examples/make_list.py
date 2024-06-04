import os
import sys
import argparse
import json

from rcdb.provider import RCDBProvider

def get_usage():
    return """
    This script prints out a run table for a given set of conditions
    
    How to use:
    1) For a single run
    python make_list.py --run=3333
    
    2) For a run range
    python make_list.py --run=3000-5000
    
    Set selection query:
    python make_list.py --run=3000-5000 --type=Production --target=LH2 --ihwp=IN

    By default, it will only print out run numbers
    To print out all information, set --show=True
    python make_list.py --run=3000-5000 --type=Production --target=LH2 --ihwp=IN --show=True
    
    One can also set multiple options for a condition
    For example,
    python make_list.py --run=3000-5000 --type=Production,Elastic
    """

def add_to_query(select_str, base_str):
    if base_str is None:
        base_str = select_str
    else:
        base_str = base_str + " and " + select_str
        
def get_list():
    
    description=""
    parser = argparse.ArgumentParser(description=description, usage=get_usage())
    parser.add_argument("--run", help="single run number or range", required=True)
    parser.add_argument("--type", type=str, help="Production, Elastic, Junk (if you want.. why not), ..")
    parser.add_argument("--target", type=str, help="LH2, LD2, Dummy")
    parser.add_argument("--config", type=str, help="DAQ config")
    parser.add_argument("--nevt", type=int, help="Minimum number of events")
    parser.add_argument("--current", type=float, help="Minimum average current")
    parser.add_argument("--ihwp", type=str, help="Insertable 1/2 wave plate IN or OUT")
    parser.add_argument("--flag", type=str, help="Good, NeedCut, Bad, Suspicious")
    parser.add_argument("--show", type=bool, help="Print option, True=show all, False=print only run numbers", default=False)
    parser.add_argument("--debug", type=bool, help="For debugging", default=False)
    args = parser.parse_args()

    # Construct a list of runs
    runs = []
    runlist=args.run
    if "-" in runlist:
        brun=runlist.split("-")[0]
        erun=runlist.split("-")[1]
        for x in range(int(brun), int(erun)+1):
            runs.append(x)
    else:
        runs.append(int(runlist))

    # DB connection - read-only copy
    con_str = "mysql://rcdb@hallcdb.jlab.org:3306/c-rcdb"
    db = RCDBProvider(con_str)

    ## Prepare the query str
    query_str = None

    # Run type
    if args.type is not None:
        args_list = [str(x) for x in args.type.split(",")]
        query_str = "run_type in %s" % args_list

    # Target
    if args.target is not None:
        select_str = "'%s' in target" % args.target
        add_to_query(select_str, query_str)

    # event count
    if args.nevt is not None:
        select_str = "event_count > %d" % (int(args.nevt))
        add_to_query(select_str, query_str)

    # beam current -- make sure to update the avg current
    if args.current is not None:
        select_str = "beam_current > %f" % (float(args.current))
        add_to_query(select_str, query_str)
        
    # run_config
    if args.config is not None:
        args_list = [str(x) for x in args.type.split(",")]
        select_str = "run_config in %s" % args_list
        add_to_query(select_str, query_str)

    # IHWP
    if args.ihwp is not None:
        select_str = "ihwp == '%s'" % args.ihwp
        add_to_query(select_str, query_str)    

    # Run flag
    if args.flag is not None:
        args_list = [str(x) for x in args.type.split(",")]        
        select_str = "run_flag in %s" % args_list
        add_to_query(select_str, query_str)            

    if query_str is None:    
        query_str = ""

    print
    print ("Query form: ", query_str)
    print

    ## Get result for the given run range
    result = db.select_runs("%s" % query_str, runs[0], runs[-1])

    ## What we want to retrieve from DB
    l_values = ["run_type", "target", "run_config", "prescales", "ihwp",
                "beam_energy", "hms_angle", "shms_angle", "hms_momentum",
                "calo_distance", "nps_fadc250_sparsification", "nps_sweeper",
                "nps_vtp_clus_readout_thr", "nps_vtp_clus_trigger_thr", "nps_vtp_pair_trigger_thr"]

    row = result.get_values(l_values)

    fout = open('list.txt', 'w')
    # Write header
    if args.show:
        ostr = "Run"
        for par_name in l_values:
            ostr = ostr + " %s" % par_name
        fout.write(ostr + '\n')

    irow = 0
    ps = {}
    for run in result:

        # For debugging
        if args.debug:
            print(run.number, row)

        if args.show:
            # form a string to write, all values
            ostr = "%s" % run.number
            for par_val in row[irow]:
                # prescales
                if "ps1" in str(par_val):
                    ps = json.loads(par_val)
                    ostr = ostr + " %s" % ps['ps1']
                    ostr = ostr + " %s" % ps['ps2']
                    ostr = ostr + " %s" % ps['ps3']
                    ostr = ostr + " %s" % ps['ps4']
                    ostr = ostr + " %s" % ps['ps5']
                    ostr = ostr + " %s" % ps['ps6']
                else:
                    ostr = ostr + "\t %s" % par_val
            fout.write(ostr + '\n')
        else:
            # write runnumbers only
            fout.write(str(run.number) + '\n')

        irow += 1

if __name__=="__main__":
    get_list()

