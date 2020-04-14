#!/usr/bin/env python3
#-*-coding: utf-8 -*-

import os
import sys
import argparse
import logging
import time

parser = argparse.ArgumentParser(prog="prun.py")
parser.add_argument("-rl", "--round_list", default="1", help="times list of rounds, for exmaple: \"1 2 4 8 16\"")
parser.add_argument("-lp", "--log_prefix", default="prun", help="prefix of log file")
parser.add_argument("-ls", "--log_suffix", default="log", help="suffix of log file")
parser.add_argument("-t", "--tag", default="%s"%os.getpid(), help="tag of t his experiement")
parser.add_argument("command", help="command need to run, command can contain {ROUND} and {NUM} variable.")

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


def expand_command(cmd, rnd, num):
    ecmd = "%s"%cmd
    while True:
        new_cmd = ecmd.replace("{ROUND}", "%s", 1)
        if new_cmd == ecmd:
            break
        new_cmd = new_cmd%rnd
        ecmd = new_cmd

    while True:
        new_cmd = ecmd.replace("{NUM}", "%s", 1)
        if new_cmd == ecmd:
            break
        new_cmd = new_cmd%num
        ecmd = new_cmd

    return ecmd
    
for r in round_list:
    times_round = int(r)

    start_time = time.time()

    logging.info("Start parallel jobs round: %d"%times_round)
    with ThreadPoolExecutor(max_workers=times_round) as executor:
        cmd_log_list = []
        for num in range(times_round):
            log_fn = "%s.%s.r%d.n%d.%s"%(args.tag, args.log_prefix, times_round, num+1, args.log_suffix)
            cmd = expand_command(args.command, times_round, num+1)
            cmd_log_list.append([cmd, log_fn])

        futures_to_job = {executor.submit(run_job, cmd_log[0], cmd_log[1]): cmd_log for cmd_log in cmd_log_list}
        for future in concurrent.futures.as_completed(futures_to_job):
            job = futures_to_job[future]
            try:
                data = future.result()
            except Exception as exc:
                print(exc)
                logging.error("Parallel job failed at round: %d!"%times_round)
                sys.exit(1)
    logging.info("End round: %d"%times_round)

    end_time = time.time()
    elp = end_time - start_time
    print("Elapsed time of this round in seconds: %.2f"%elp)
    print("-"*48)
    print("")

