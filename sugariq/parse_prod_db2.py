#!/usr/bin/env python3

import json
from math import floor
import csv
import argparse
import sys

'''
This file parses 4 data files that were retrieved using db2 queries similar to:

#/bin/sh 
source /home/db2inst1/sqllib/db2profile

db2 "connect to MDTDB user db2dat01 using SECRET_PASSWORD"

db2 "EXPORT TO sgabove.csv OF DEL MODIFIED BY COLDEL0X09 select person_id, date(PUMP_TIME_TS), count(*) as ABOVE from (select distinct person_id, pump_time_ts from CLEANSG.USERSG where CREATED_AT >= (CURRENT_TIMESTAMP - 10 DAYS) and SGMGDL > 180) group by person_id, date(PUMP_TIME_TS) order by person_id, date(PUMP_TIME_TS)"

db2 "EXPORT TO sgbelow.csv OF DEL MODIFIED BY COLDEL0X09 select person_id, date(PUMP_TIME_TS), count(*) as BELOW from (select distinct person_id, pump_time_ts from CLEANSG.USERSG where CREATED_AT >= (CURRENT_TIMESTAMP - 10 DAYS) and SGMGDL < 70) group by person_id, date(PUMP_TIME_TS) order by person_id, date(PUMP_TIME_TS)"

db2 "EXPORT TO sgtotal.csv OF DEL MODIFIED BY COLDEL0X09 select person_id, date(PUMP_TIME_TS), count(*) as TOTAL from (select distinct person_id, pump_time_ts from CLEANSG.USERSG where CREATED_AT >= (CURRENT_TIMESTAMP - 10 DAYS)) group by person_id, date(PUMP_TIME_TS) order by person_id, date(PUMP_TIME_TS)"

db2 "EXPORT TO sgjson.csv OF DEL MODIFIED BY COLDEL0X09 select distinct * from ANALYTICS.MYDATA_ENTRIES where CREATED_AT >= (CURRENT_TIMESTAMP - 10 DAYS) and PERIOD_TYPE='ONE_DAY'"

'''
# edit the variables in the next section

exclude_dates = [ 20190422, 20190421 ]
exclude_before_date = 20190414 # as int
pct_limit = 5.0

ABOVE_FILE = 'sgabove.csv'
BELOW_FILE = 'sgbelow.csv'
TOTAL_FILE = 'sgtotal.csv'
JSON_FILE = 'sgjson.csv'

# None for no csv file
csv_file = 'prod_for_excel.csv' 

# end of edits

if csv_file is not None:
    csv_out = open(csv_file, 'w')
    csvwriter = csv.writer(csv_out)
    csvwriter.writerow([ 'person_id', 'date', 'last_date', 'totalCnt', 'sensorCnt',
                         'js_above', 'js_below', 'js_in',
                         'calc_above', 'calc_below', 'calc_in' ])

# json data
js = {}
with open(JSON_FILE) as f:
    for line in f:
        if line.startswith('-'):
            continue
        g = line.split()
        if len(g) != 13:
            continue
        if g[7].startswith('"'):
            g[7] = g[7].replace('""', '"')
            g[7] = g[7][1:-1]
        if not g[7].startswith('{'):
            continue
        j = json.loads(g[7])
        if j['timeInRangeSummary']['aboveRange'] < 0:
            continue
        pid = int(g[1])
        date = int(g[2])
        #if date in exclude_dates:
        #continue
        if pid not in js:
            js[pid] = {}
        if date not in js[pid]:
            js[pid][date] = { 'pct': {}}
        js[pid][date]['pct']['above'] = j['timeInRangeSummary']['aboveRange']
        js[pid][date]['pct']['below'] = j['timeInRangeSummary']['belowRange']
        js[pid][date]['pct']['in'] = j['timeInRangeSummary']['inRange']
        js[pid][date]['sensorWearTime'] = j['sensorWearTime']
        js[pid][date]['sensorCnt'] = int(j['sensorWearTime'] / 5)

#print(json.dumps(js, indent=2, sort_keys=True))

calc = {}      
# above
with open(ABOVE_FILE) as f:
    for line in f:
        if line.startswith('person'):
            continue
        g = line.split()
        pid = int(g[0])
        date = int(g[1])
        #if date in exclude_dates or int(date) <= exclude_before_date:
        #    continue
        cnt = int(g[2])
        if pid not in calc:
            calc[pid] = {}
        if date not in calc[pid]:
            calc[pid][date] = {}
        else:
            print('DUPLICATE MYDATA!! {} {}'.format(pid, date))
        calc[pid][date]['aboveCnt'] = cnt
        calc[pid][date]['belowCnt'] = 0
        
# below
with open(BELOW_FILE) as f:
    for line in f:
        if line.startswith('person'):
            continue
        g = line.split()
        pid = int(g[0])
        date = int(g[1])
        #if date in exclude_dates or int(date) <= exclude_before_date:
        #    continue
        cnt = int(g[2])
        if pid not in calc:
            calc[pid] = {}
        if date not in calc[pid]:
            calc[pid][date] = {}
        calc[pid][date]['belowCnt'] = cnt
        if 'aboveCnt' not in calc[pid][date]:
            calc[pid][date]['aboveCnt'] = 0

# total
with open(TOTAL_FILE) as f:
    for line in f:
        if line.startswith('person'):
            continue
        g = line.split()
        pid = int(g[0])
        date = int(g[1])
        #if date in exclude_dates or int(date) <= exclude_before_date:
        #    continue
        cnt = int(g[2])
        if pid not in calc:
            calc[pid] = {}
        if date not in calc[pid]:
            calc[pid][date] = {}
        calc[pid][date]['totalCnt'] = cnt
        if 'aboveCnt' not in calc[pid][date]:
            calc[pid][date]['aboveCnt'] = 0
        if 'belowCnt' not in calc[pid][date]:
            calc[pid][date]['belowCnt'] = 0
        calc[pid][date]['pct'] = {
            'above': floor(100.0 * calc[pid][date]['aboveCnt'] / cnt),
            'below': floor(100.0 * calc[pid][date]['belowCnt'] / cnt) }
        calc[pid][date]['pct']['in'] = 100 - calc[pid][date]['pct']['above'] - calc[pid][date]['pct']['below']

#print(json.dumps(calc, indent=2, sort_keys=True))

# stats

# calculate last date for each user
last_date = {}
for pid in calc:
    last_date[pid] = sorted(calc[pid].keys())[-1]

gtotal = 0
gdiff = 0
gdiff_pct_limit = 0
for pid in calc:
    ptotal = 0
    pdiff = 0
    pdiff_pct_limit = 0
    for date in calc[pid]:
        if date in exclude_dates or date <= exclude_before_date:
            continue
        if pid not in js or date not in js[pid]:
            print('ERROR no matching js data {} {}'.format(pid, date))
            continue
        ptotal += 1
        if js[pid][date]['pct'] != calc[pid][date]['pct']:
            print('MISMATCH1 data pid={} date={} totalCnt={} sensorCnt={}'.format(pid, date, calc[pid][date]['totalCnt'], js[pid][date]['sensorCnt']))
            print('MISMATCH2 js   {}', json.dumps(js[pid][date]['pct'], sort_keys=True))
            print('MISMATCH3 calc {}', json.dumps(calc[pid][date]['pct'], sort_keys=True))
            pdiff += 1
            if abs(calc[pid][date]['pct']['in'] - js[pid][date]['pct']['in']) > pct_limit:
                pdiff_pct_limit += 1
        # csv out
        if csv_file:
            csvwriter.writerow([ pid, date, last_date[pid], calc[pid][date]['totalCnt'], js[pid][date]['sensorCnt'],
                                 js[pid][date]['pct']['above'], js[pid][date]['pct']['below'], js[pid][date]['pct']['in'], 
                                 calc[pid][date]['pct']['above'], calc[pid][date]['pct']['below'], calc[pid][date]['pct']['in'] ])
    gtotal += ptotal
    gdiff += pdiff
    gdiff_pct_limit += pdiff_pct_limit
    print('pid = {}, ptotal={}, pdiff={}, pdiff_pct_limit={}'.format(pid, ptotal, pdiff, pdiff_pct_limit))

# print globals
print('gtotal={}, gdiff={}, gdiff_pct_limit={}'.format(gtotal, gdiff, gdiff_pct_limit))

if csv_file:
    csv_out.close()
