#!/usr/bin/env python3
#-*-coding: utf-8 -*-

import os
import sys
import argparse
import logging

parser = argparse.ArgumentParser(prog="prun.py")
parser.add_argument("-rl", "--round_list", default="1", help="times list of rounds, for exmaple: \"1 2 4 8 16\"")
parser.add_argument("-lp", "--log_prefix", default="prun", help="prefix of log file")
parser.add_argument("-ls", "--log_suffix", default="log", help="suffix of log file")
parser.add_argument("-t", "--tag", default="%s"%os.getpid(), help="tag of t his experiement")
parser.add_argument("command", help="command need to run")

args=parser.parse_args()

logging.basicConfig(format="[PRUN %(asctime)s %(levelname)s] %(message)s",
    datefmt="%d-%m-%Y %H:%M:%S", level=logging.INFO)

import threading
import concurrent
from concurrent.futures import ThreadPoolExecutor
import subprocess

round_list = args.round_list.split()

def run_job(cmd, logfile):
    logging.info("Running job: \"%s\", output: %s"%(cmd, logfile))
    proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
           env=os.environ)
    fp = open(logfile, "w")
    assert(fp)
    for line in proc.stdout.readlines():
        fp.write(line.decode("utf-8"))
    retval = proc.wait()
    return retval

for r in round_list:
    times_round = int(r)

    logging.info("Start parallel jobs round: %d"%times_round)
    with ThreadPoolExecutor(max_workers=times_round) as executor:
        log_fn_list = []
        for num in range(times_round):
            log_fn = "%s.%s.r%d.n%d.%s"%(args.tag, args.log_prefix, times_round, num+1, args.log_suffix)
            log_fn_list.append(log_fn)
        futures_to_job = {executor.submit(run_job, args.command, log_fn): log_fn for log_fn in log_fn_list}
        for future in concurrent.futures.as_completed(futures_to_job):
            job = futures_to_job[future]
            try:
                data = future.result()
            except Exception as exc:
                print(exc)
                logging.error("Parallel job failed at round: %d!"%times_round)
                sys.exit(1)
    logging.info("End round: %d"%times_round)

