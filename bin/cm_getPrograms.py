import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from ConfigurationClient import *
import argparse

# Parsing arguments
description = "Get all programs for a given instrument/semester"
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-instrument', '-i', default=None, help='instrument', required=True)
parser.add_argument('-semester', default=None, help='Semester', required = False)
parser.add_argument('-progname', '-p', default=None, help='Program name', required=False)

if __name__ == '__main__':
    args = parser.parse_args()
    instrument_class = get_instrument_class(args.instrument)
    instrument_class.get_all_configs(semester=args.semester, progname=args.progname)

