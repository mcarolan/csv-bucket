#!/usr/bin/python
from optparse import OptionParser
import sys
import csv
import time
import calendar
from decimal import Decimal

#greatfully lifted from http://stackoverflow.com/questions/6556078/how-to-read-a-csv-file-from-a-stream-and-process-each-line-as-it-is-written
class ReadlineIterator:
    """An iterator that calls readline() to get its next value."""
    def __init__(self, f): self.f = f
    def __iter__(self): return self
    def next(self):
        line = self.f.readline()
        if line: return line
        else: raise StopIteration

def fail(message):
	sys.stderr.write(message)
	sys.exit(1)

def monthly_bucket_function(date):
	return "%s %d" % (calendar.month_name[date.tm_mon], date.tm_year)

def weekly_bucket_function(date):
	daysInMonth = calendar.monthrange(date.tm_year, date.tm_mon)[1]
	week = max(date.tm_mday / (daysInMonth / 4), 1)
	return "Week %d %s %d" % (week, calendar.month_name[date.tm_mon], date.tm_year)

#parse command line arguments
if __name__ != "__main__":
	fail("Errm, don't import me")

parser = OptionParser()

parser.add_option("-m", "--mode", default="monthly", help="Bucketing mode. May be weekly or monthly, monthly is default")
parser.add_option("-d", "--date-column", default=0, type="int", help="Column number in which date values are stored. Zero indexed. Default is 0.")
parser.add_option("-v", "--value-column", default=2, type="int", help="Column number in which the values to be aggregated are stored. Zero indexed. Default is 2.")
parser.add_option("-f", "--date-format", default="%Y-%m-%d", help="Date format. Default is %Y-%m-%d. Information at http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior")
parser.add_option("-x", action="store_false", dest="skip_header", help="If present will not skip the header row of data.", default=True)

(options, args) = parser.parse_args()

bucketFunction = None

if options.mode == "monthly":
	bucketFunction = monthly_bucket_function
elif options.mode == "weekly":
	bucketFunction = weekly_bucket_function
else:
	fail("Mode must either be monthly or weekly, instead I got " + options.mode)

#read data from stdin
data = []
reader = csv.reader(ReadlineIterator(sys.stdin))
firstRow = True
for row in reader:
	if firstRow and options.skip_header:
		firstRow = False
		continue
	firstRow = False

	numberOfColumns = len(row)

	if options.date_column >= numberOfColumns:
		fail("Date column out of range in data, date column is %d, there are %d columns" % (options.date_column, numberOfColumns))

	if options.value_column >= numberOfColumns:
		fail("Value column out of range in data, value column is %d, there are %d columns" % (options.value_column, numberOfColumns))

	date = time.strptime(row[options.date_column], options.date_format)
	value = Decimal(row[options.value_column])

	data.append((date, value))

#bucket!
dict = {}

for datum in data:
	bucket = bucketFunction(datum[0])

	if not bucket in dict:
		dict[bucket] = 0

	dict[bucket] += datum[1]

print "bucket,value"
for bucket in dict.keys():
	value = dict[bucket]

	print "%s,%d" % (bucket, value)