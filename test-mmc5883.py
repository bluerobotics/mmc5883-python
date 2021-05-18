#!/usr/bin/python3

import argparse
from mmc5883 import MMC5883
from time import sleep, time

parser = argparse.ArgumentParser(description='mmc5883 test')
parser.add_argument('--output', action='store', type=str, default=None)
parser.add_argument('--frequency', action='store', type=int, default=None)
args = parser.parse_args()

mmc = MMC5883()

if args.output:
    outfile = open(args.output, "w")

if args.output:
    outfile.write(output)
    outfile.write('\n')

while True:
    data = mmc.measure()
    output = f"{time()} 1 {data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x} {data.y} {data.z} {data.t}"
    print(output)
    if args.output:
        outfile.write(output)
        outfile.write('\n')
    if args.frequency:
        sleep(1.0/args.frequency)

# this is never reached, but works anyway in practice
# todo handle KeyboardInterrupt for ctrl+c
if args.output:
    outfile.close()
