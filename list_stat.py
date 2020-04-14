#!/usr/bin/env python3
#-*-coding: utf-8 -*-

import os
import sys
import argparse
import logging

parser = argparse.ArgumentParser(prog="list_stat.py", description="give basic statistics of a numeric list")
parser.add_argument("-lb", "--low_boundary", type=float, help="filter list with low boundary limit")
parser.add_argument("-hb", "--high_boundary", type=float, help="filter list with high boundary limit")

args=parser.parse_args()


num_list = []
for line in sys.stdin:
    line = line.strip()
    num_list.append(float(line))

sum_keep = 0
num_list_keep = []
num_list_throw = []
for num in num_list:
    if args.low_boundary and num<args.low_boundary:
        num_list_throw.append(num)
        continue
    if args.high_boundary and num>args.high_boundary:
        num_list_throw.append(num)
        continue
    num_list_keep.append(num)
    sum_keep = sum_keep + num


avg_keep = 0
if num_list_keep:
    avg_keep = sum_keep/len(num_list_keep)
    num_list_keep.sort()
    print("Numbers kept: %d"%len(num_list_keep))
    print("Sum kept: %.2f"%(sum_keep))
    print("Avg kept: %.2f"%(avg_keep))
    print("Lowest kept: %.2f"%(num_list_keep[0]))
    print("Higest kept: %.2f"%(num_list_keep[-1]))
    print("Throw numbers: %s"%(" ".join(map(lambda x:"%.2f"%x, num_list_throw)))) 
else:
    print("Empty filtered numeric list.")
    sys.exit(1)


