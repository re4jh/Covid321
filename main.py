#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, line-too-long

import csv
import math
import sys
import time
import argparse
import os.path
import requests
from tabulate import tabulate

CSV_DATA_URL = 'https://pavelmayer.de/covid/risks/data.csv'
DATA_FILE = 'data/data.csv'

if not os.path.isfile(DATA_FILE) or time.time() - os.path.getmtime(DATA_FILE) > 3600:
    CSV_DATA_FILE = requests.get(CSV_DATA_URL, allow_redirects=True)
    if CSV_DATA_FILE.status_code == 200:
        open(DATA_FILE, 'wb').write(CSV_DATA_FILE.content)

if not os.path.isfile(DATA_FILE):
    print('Could not download new csv-data and there is not even old data. I quit!')
    sys.exit()

parser = argparse.ArgumentParser(
    description='Read data from pavelmayer.de\'s Covid-Risk-Table and count days until treshold.')
parser.add_argument('-t', '--treshold', default=50, help=r'treshold for cases/100k in x days')
parser.add_argument('-c', '--cases', default=0, help=r'set a minimum of cases/100k as filter')
parser.add_argument('-r', '--repro', default=0, help=r'set a minimum of reproduction/week as filter')

args = parser.parse_args()

L_TABLE = []

with open(DATA_FILE) as csv_file:
    CSV_READER = csv.reader(csv_file, delimiter=',')
    LINE_COUNT = 0
    for row in CSV_READER:
        if LINE_COUNT == 0:
            L_TABLE.append(['Name', 'Bundesland', 'Fälle/100k', 'RwK', str(args.treshold) + 'inW', str(args.treshold) + 'inD'])
            LINE_COUNT += 1
        else:
            if row[1] == row[10]:
                row[1] = 'B ' + row[1]
            if (float(row[16]) > 0 and float(row[23]) > 1) or (float(row[16]) > args.treshold and float(row[23]) != 1):
                to_treshold = float(float(args.treshold) / float(row[16]))
                log_to_treshold = math.log(to_treshold)
                log_rwk = math.log(float(row[23]))
                weeks_left = '∞'
                extra_prefix = ''
                if float(row[16]) > float(args.treshold) and float(row[23]) < 1:
                    extra_prefix = '--'
                if log_rwk != 0:
                    weeks_left = str(round(float(log_to_treshold / log_rwk), 4))
                if float(row[16])>=float(args.cases) and float(row[23])>=float(args.repro):
                    L_TABLE.append([row[1], row[10], str(round(float(row[16]), 3)), str(round(float(row[23]), 3)), extra_prefix + weeks_left, extra_prefix + str(round(float(weeks_left) * 7, 2))])
                LINE_COUNT += 1
            else:
                if float(row[16])>=float(args.cases) and float(row[23])>=float(args.repro):
                    L_TABLE.append([row[1], row[10], str(round(float(row[16]), 3)), str(round(float(row[23]), 3)), '∞', '∞'])

print(tabulate(L_TABLE, tablefmt="psql", headers="firstrow"))
