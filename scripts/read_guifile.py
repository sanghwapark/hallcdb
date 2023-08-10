import os, sys

from hallc_rcdb import parser

def main(fin):
    this_info = parser.runinfo_parser(fin)
    print(this_info)

if __name__=="__main__":
    main(sys.argv[1])
