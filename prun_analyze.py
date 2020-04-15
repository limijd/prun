#!/usr/bin/env python3
#-*-coding: utf-8 -*-

import os
import sys
import argparse

parser = argparse.ArgumentParser(prog="prun_analyze.py", description="analyze all prun logs")
parser.add_argument('PRUN_LOG_FILES', type=argparse.FileType('r'), nargs='+')
parser.add_argument("-lb", "--low_boundary", type=float, default=0, help="filter list with low boundary limit")
args=parser.parse_args()


rounds = {}

for fn in args.PRUN_LOG_FILES:
    name = fn.name

    parts = name.split(".")
    tag,num,rnd = ".".join(parts[:-4]), parts[-2], parts[-3]
    assert(num[0]=="n")
    assert(rnd[0]=="r")
    num=int(num[1:])
    rnd=int(rnd[1:])
    
    fp = open(name, "r")
    ut=0
    st=0
    rt=0
    for line in fp.readlines():
        if line.find("user ") == 0:
            line=line.strip()
            ut = float(line.split()[1])
        if line.find("sys ") == 0:
            line=line.strip()
            st = float(line.split()[1])
        if line.find("real ") == 0:
            line=line.strip()
            rt = float(line.split()[1])

    if rnd in rounds:
        assert(num not in rounds[rnd])
        rounds[rnd][num] = [rt, ut , st]
    else:
        rounds[rnd]={num:[rt,ut,st]}

results={}

for rnd, rdata in rounds.items():
    r_total = 0
    r_avg = 0
    r_min= 0
    r_max = 0x7fffffff
    num_kept = []
    num_skipped = []
    for num, perfdata in rdata.items():
        t = perfdata[1] + perfdata[2]
        r_total = r_total + t
        if t<args.low_boundary:
            num_skipped.append(num)
            continue
        else:
            num_kept.append(num)
        if t>r_max:
            r_max = t
        if t<r_min:
            r_min = t
    r_avg=r_total/len(num_kept)
    results[rnd] = [rnd, r_total, r_avg, r_max, r_min, num_kept, num_skipped]

keys = list(results.keys())
keys.sort()

for k in keys:
    rnd, r_total, r_avg, r_max, r_min, num_kept, num_skipped = results[k]
    assert(rnd==k)
    print("[Round: %4d] Total CPU: %.2f, Avg: %.2f, Min: %.2f, Max: %.2f, Kept: %d, Skipped: %d"%(k, r_total, r_avg, r_max, r_min, len(num_kept), len(num_skipped)))
