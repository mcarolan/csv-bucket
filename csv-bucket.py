#!/usr/bin/python
from optparse import OptionParser
import sys
import csv
import calendar
import datetime
from decimal import Decimal

#credit to http://stackoverflow.com/questions/6556078/how-to-read-a-csv-file-from-a-stream-and-process-each-line-as-it-is-written
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
	return "%s %d" % (calendar.month_name[date.month], date.year)

#credit to http://stackoverflow.com/questions/739241/date-ordinal-output
def day_with_suffix(day):
	if 4 <= day <= 20 or 24 <= day <= 30:
		return str(day) + "th"
	else:
 		return str(day) + ["st", "nd", "rd"][day % 10 - 1]

def weekly_bucket_function(date):
	day = date.day
	month = date.month
	year = date.year

	monthCalendar = calendar.monthcalendar(year, month)
	week = next(w for w in monthCalendar if (day in w))

	firstDayOfWeek = week[0]
	lastDayOfWeek = week[-1]
	
	noneZeroWeekEntries = filter(lambda d: d != 0, week)
	overlapSize = len(week) - len(noneZeroWeekEntries)

	weekStart = None
	weekEnd = None

	if firstDayOfWeek == 0:
		weekStart = datetime.date(year, month, noneZeroWeekEntries[0]) - datetime.timedelta(overlapSize)
	else:
		weekStart = datetime.date(year, month, firstDayOfWeek)

	if lastDayOfWeek == 0:
		weekEnd = datetime.date(year, month, noneZeroWeekEntries[-1]) + datetime.timedelta(overlapSize)
	else:
		weekEnd = datetime.date(year, month, lastDayOfWeek)

	return "%s %s %d to %s %s %d" % (day_with_suffix(weekStart.day), calendar.month_name[weekStart.month], weekStart.year, day_with_suffix(weekEnd.day), calendar.month_name[weekEnd.month], weekEnd.year)

#parse command line arguments
if __name__ != "__main__":
	fail("Errm, don't import me")

parser = OptionParser()

parser.add_option("-m", "--mode", default="monthly", help="Bucketing mode. May be weekly or monthly, monthly is default")
parser.add_option("-d", "--date-column", default=0, type="int", help="Column number in which date values are stored. Zero indexed. Default is 0.")
parser.add_option("-v", "--value-column", default=2, type="int", help="Column number in which the values to be aggregated are stored. Zero indexed. Default is 2.")
parser.add_option("-f", "--date-format", default="%Y-%m-%d", help="Date format. Default is %Y-%m-%d. Information at http://docs.python.org/2/library/datetime.html#strftime-strptime-behavior")
parser.add_option("-n", action="store_false", dest="skip_header", help="No header - the first row of data will not be skipped", default=True)
parser.add_option("-b", "--begin-date", default="1900-01-01", help="The date of which filtering should begin at. This is in the same format as provided to --date-format. Default is 1900-01-01")
parser.add_option("-e", "--end-date", default="3000-01-01", help="The date of which filtering should end at. This is in the same format as provided to --date-format. Default is 3000-01-01")

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

	date = datetime.datetime.strptime(row[options.date_column], options.date_format)
	value = Decimal(row[options.value_column])

	data.append((date, value))

#filter!
beginDate = datetime.datetime.strptime(options.begin_date, options.date_format)
endDate = datetime.datetime.strptime(options.end_date, options.date_format)

data = filter(lambda d: d[0] >= beginDate and d[0] < endDate, data)

#bucket!
bucketed = []

for datum in data:
	bucket = bucketFunction(datum[0])

	#create a new bucket for this datum!
	if len(bucketed) == 0 or bucketed[-1][0] != bucket:
		bucketed.append((bucket, datum[1]))
	else:
		bucketed[-1] = (bucket, bucketed[-1][1] + datum[1])

print "bucket,value"
for bucket in bucketed:
	print "%s,%0.2f" % (bucket[0], bucket[1])