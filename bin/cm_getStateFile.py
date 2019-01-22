import os, sys, inspect
currentdir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parentdir = os.path.dirname(currentdir)
sys.path.insert(0,parentdir)

from ConfigurationClient import *
import argparse

# Parsing arguments
description = "Get a state file for instrument/semester/program/state_name"
parser = argparse.ArgumentParser(description=description)
parser.add_argument('-instrument', '-i', default=None, help='instrument', required=True)
parser.add_argument('-semester', '-s', default=None, help='Semester', required = False)
parser.add_argument('-progname', '-p', default=None, help='Program name', required=False)
parser.add_argument('-state_name', '-name', '-n', default=None, help='State name', required=False)

if __name__ == '__main__':
    args = parser.parse_args()
    instrument_class = get_instrument_class(args.instrument.upper())
    instrument_class.get_state_file(semester=args.semester, progname=args.progname, statenam=args.state_name)

