
import csv
import sys
import datetime
import argparse

import dateutil.parser
import matplotlib.pyplot as plt
import matplotlib.dates

parser = argparse.ArgumentParser(description="Plot CSV data captured by peaktech-2025.py")
parser.add_argument("file", metavar="FILE", type=str, nargs="?",
                    help="input file, default stdin")
parser.add_argument("--output", const=sys.stdout, nargs="?",
                    help="save plot to file, default stdout")
parser.add_argument("--format", default="pdf",
                    help="output file format, default PDF")
args = parser.parse_args()

if args.file:
    with open(args.file) as fd:
        lines = fd.readlines()
else:
    lines = sys.stdin

reader = csv.reader(lines, delimiter=",")
time_series = []
value_series = []
y_unit = None

for record in reader:
    if not y_unit:
        y_unit = record[2]
    time_series.append(dateutil.parser.parse(record[0]))
    value_series.append(float(record[1]))

time_series = matplotlib.dates.date2num(time_series)

fig = plt.figure()
if args.file:
    plt.title(args.file)
plt.plot_date(time_series, value_series, marker=".", ms=1.5)
plt.ylabel(y_unit)
plt.tick_params(axis="x", labelsize=8)
plt.grid(which='major', axis='both')

axes = plt.axes()
date_locator = axes.xaxis.get_major_locator()
date_formatter = matplotlib.dates.AutoDateFormatter(date_locator)
date_formatter.scaled[1/(24.*60.)] = "%H:%M:%S"
axes.xaxis.set_major_formatter(date_formatter)

if args.output:
    fig.savefig(args.output, format=args.format)
else:
    plt.show()
