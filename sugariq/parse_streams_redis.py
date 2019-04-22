#!/usr/bin/env python3

import json
import argparse
import re

conv0 = re.compile(r'{([A-Za-z][^:"]+?)([=:])')
conv1 = re.compile(r',([^,"]*?[a-zA-Z][^,"]*?)([=:])')
conv2 = re.compile(r':([A-Za-z]+),')
conv3 = re.compile(r'\(([^\)]+)\)')
conv4 = re.compile(r'"(false|true)"')
def parse_file(fname):
    with open(fname) as f:
        for line in f:
            if line.startswith('History') or line.startswith('Current'):
                continue
            if not line.startswith('[{'):
                raise Exception('Unrecognized line : {}'.format(line))

            line = re.sub(conv0, r'{"\1":', line)
            line = re.sub(conv1, r',"\1":', line)
            line = re.sub(conv2, r':"\1",', line)
            line = re.sub(conv3, r'[\1]', line)
            line = re.sub(conv4, r'\1', line)
            js = json.loads(line)
            yield js

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='parse streams redis dump')
    parser.add_argument('-f', '--filename', required=True, help='redis data file')
    parser.add_argument('-j', '--json', help='output as json array', action='store_true')
    args = parser.parse_args()

    if args.json:
        print(json.dumps(list(parse_file(args.filename)), indent=2, sort_keys=True))
    else:
        for js in parse_file(args.filename):
            print(json.dumps(js, indent=2, sort_keys=True))
