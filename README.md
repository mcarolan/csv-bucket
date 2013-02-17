csv-bucket
==========

Aggregate a column of data in a CSV file over certain time buckets.

I'm using this to track what I spend. I get a CSV dump of my spend from an app called toshl, tagged like so:

<pre>
"Date","Entry (tags)","Expense amount","Currency","Description"
"2013-02-17","insurance","9.99","GBP",""
"2013-02-17","coke","1.5","GBP",""
"2013-02-16","booze","3.6","GBP",""
"2013-02-16","booze","3.6","GBP",""
...
</pre>

I can then use csv-bucket to aggregate this data over calendar weeks or months. E.g.

<pre>
$ cat input.csv | grep booze | ./csv-bucket.py --mode weekly -n
bucket,value
11th February 2013 to 17th February 2013,36.85
4th February 2013 to 10th February 2013,18.50
28th January 2013 to 3rd February 2013,37.90
21st January 2013 to 27th January 2013,10.18
</pre>

Or

<pre>
$ cat input.csv | grep booze | ./csv-bucket.py --mode monthly -n
bucket,value
February 2013,78.75
January 2013,24.68
</pre>

I can then make a pretty graph showing my slow decent into alcoholism 
