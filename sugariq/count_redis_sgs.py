#!/usr/bin/python3

import argparse
import json

parser = argparse.ArgumentParser('count sgs from redis json')
parser.add_argument('-f'. '--fname', required=True, help='redis json filename')
args = parser.parse_args()

with open(args.fname) as f:
    js = json.load(f)

day_cnt = {}
for day in js:
    for e in day:
        #print(json.dumps(e, indent=2))
        date = e['PUMP_TIME'].split('T')[0]
        if 'intValues' in e and 'SG_mgdL' in e['intValues']:
            if date not in day_cnt:
                day_cnt[date] = 1
            else:
                day_cnt[date] += 1

print(json.dumps(day_cnt, indent=2, sort_keys=True))
