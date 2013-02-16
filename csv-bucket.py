#!/usr/bin/python
from optparse import OptionParser
import sys

if __name__ != "__main__":
	sys.stderr.write("Errm, don't import me") 
	sys.exit(1)

parser = OptionParser()

parser.add_option("-m", "--mode", default="monthly", help="Bucketing mode. May be weekly or monthly, monthly is default")

(options, args) = parser.parse_args()

if options.mode != "monthly" and options.mode != "weekly":
	sys.stderr.write("Mode must either be monthly or weekly, instead I got " + options.mode)
	sys.exit(2)