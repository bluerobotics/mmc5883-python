#!/usr/bin/python3

import argparse
from mmc5883 import MMC5883
import signal
from time import sleep, time

parser = argparse.ArgumentParser(description='mmc5883 test')
parser.add_argument('--output', action='store', type=str, default=None)
parser.add_argument('--frequency', action='store', type=int, default=None)
args = parser.parse_args()

mmc = MMC5883()

outfile = None

if args.output:
    outfile = open(args.output, "w")

def cleanup(_signo, _stack):
    if outfile:
        outfile.close()
    exit(0)


signal.signal(signal.SIGTERM, cleanup)
signal.signal(signal.SIGINT, cleanup)

while True:
    data = mmc.measure()
    output = f"{time()} 1 {data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x} {data.y} {data.z} {data.t}"
    print(output)
    if outfile:
        outfile.write(output)
        outfile.write('\n')
    if args.frequency:
        sleep(1.0/args.frequency)
