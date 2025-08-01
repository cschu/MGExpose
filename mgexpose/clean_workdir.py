#!/usr/bin/env python

""" Module to clean nextflow workdir """

import argparse
import csv
import os
import re


def main():
    """ Main. """
    ap = argparse.ArgumentParser()
    ap.add_argument("workdir")
    ap.add_argument("tracefile")
    args = ap.parse_args()

    with open(args.tracefile, "rt", encoding="UTF-8") as _in:
        keep = set(
            row["hash"]
            for row in csv.DictReader(_in, delimiter="\t")
            if row["status"] in ("CACHED", "COMPLETED")
        )

    # level2 = args.workdir.rstrip("/").count("/") + 2
    walk = os.walk(args.workdir)
    wd, dirs, _ = next(walk)
    for d in dirs:
        if re.match(r'^[0-9a-f]{2}$', d):
            _, subdirs, _ = next(os.walk(os.path.join(wd, d)))
            for sd in subdirs:
                wd_hash = f"{d}/{sd[:6]}"
                if wd_hash in keep:
                    print(f"keeping {os.path.join((wd, d, sd))}")

    # for wd, _, _ in os.walk(args.workdir):
    # 	if wd.count("/") == level2:
    # 		# 03/717392
    # 		# work/81/9299777e91fb27fb6626980719cf1f
    # 		wd_hash = wd[len(args.workdir.rstrip("/")) + 1:][:9]
    # 		if wd_hash not in keep:
    # 			# print(f"removing {wd}")
    # 			...
    # 		else:
    # 			print(f"keeping {wd}")


if __name__ == "__main__":
    main()
