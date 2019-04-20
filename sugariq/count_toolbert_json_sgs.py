#!/usr/bin/python

import argparse
import json

parser = argparse.ArgumentParser(description='count sgs per day')
parser.add_argument('-f','--fname', required=True, help='toolbert json input file')
args = parser.parse_args()

with open(args.fname) as f:
    js = json.load(f)

sg_counts = {}
for entry in js:
    for v in entry['value']:
        for sg in v.get('sgs', []):
            date = sg['dateTime'].split('T')[0]
            if date not in sg_counts:
                sg_counts[date] = 1
            else:
                sg_counts[date] += 1

print(json.dumps(sg_counts, indent=2, sort_keys=True))


            

            
