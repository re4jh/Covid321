#!/usr/bin/python3
# -*- coding: utf-8 -*-
# pylint: disable=missing-docstring, line-too-long

import csv
import math
import time
import os.path
import requests
from cli_tables.cli_tables import *

CSV_DATA_URL = 'https://pavelmayer.de/covid/risks/data.csv'
DATA_FILE = 'data/data.csv'

if not os.path.isfile(DATA_FILE) or time.time() - os.path.getmtime(DATA_FILE) > 3600:
    CSV_DATA_FILE = requests.get(CSV_DATA_URL, allow_redirects=True)
    if CSV_DATA_FILE.status_code == 200:
        open(DATA_FILE, 'wb').write(CSV_DATA_FILE.content)

if not os.path.isfile(DATA_FILE):
    print('Could not download new csv-data and there is not even old data. I quit!')
    sys.exit()

L_TABLE = []

with open(DATA_FILE) as csv_file:
    CSV_READER = csv.reader(csv_file, delimiter=',')
    LINE_COUNT = 0
    for row in CSV_READER:
        if LINE_COUNT == 0:
            L_TABLE.append(['Name', 'Fälle/100k', 'RwK', '50inW', '50inD'])
            LINE_COUNT += 1
        else:
            if float(row[16]) > 0 and float(row[23]) > 1:
                to_fifty = float(50 / float(row[16]))
                log_to_fifty = math.log(to_fifty)
                log_rwk = math.log(float(row[23]))
                weeks_left = '∞'
                if log_rwk != 0:
                    weeks_left = str(round(float(log_to_fifty/log_rwk), 4))
                L_TABLE.append([row[1], str(round(float(row[16]), 3)), str(round(float(row[23]), 3)), weeks_left, str(round(float(weeks_left)*7, 2))])
                LINE_COUNT += 1
            else:
                L_TABLE.append([row[1], str(round(float(row[16]), 3)), str(round(float(row[23]), 3)), '∞', '∞'])


print_table(L_TABLE, double_hline=True)
