#!/usr/bin/python3

import argparse
from mmc5883 import MMC5883
from pathlib import Path
import llog
import time

device = "mmc5883"
defaultMeta = Path(__file__).resolve().parent / f"{device}.meta"

parser = argparse.ArgumentParser(description=f'{device} test')
parser.add_argument('--output', action='store', type=str, default=None)
parser.add_argument('--meta', action='store', type=str, default=defaultMeta)
parser.add_argument('--frequency', action='store', type=int, default=None)
args = parser.parse_args()


with llog.LLogWriter(args.meta, args.output) as log:
    mmc = MMC5883()

    while True:
        data = mmc.measure()
        log.log(llog.LLOG_DATA, f"{data.x_raw} {data.y_raw} {data.z_raw} {data.t_raw} {data.x} {data.y} {data.z} {data.t}")
        
        if args.frequency:
            time.sleep(1.0/args.frequency)
