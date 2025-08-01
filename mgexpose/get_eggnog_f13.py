#!/usr/bin/env python
# pylint: disable=C0301,R0801
# flake8: noqa

""" Get emapper data from database. """

import argparse
import os
import pathlib

import pandas as pd

from db import read_db_details, DbEmapperResult


def main():
    """ Main. """
    ap = argparse.ArgumentParser()
    ap.add_argument("database", type=str)
    ap.add_argument("credentials", type=str)
    ap.add_argument("--project_id", type=str)
    ap.add_argument("--sample_name", type=str)
    ap.add_argument("--bulk_file", type=str)
    ap.add_argument("--sample_tax_map", type=str)
    ap.add_argument(
        "--fill_missing",
        action="store_true",
        help="Generate empty annotation file if genome does not have a database record.",
    )

    args = ap.parse_args()

    db_access = read_db_details(args.credentials)[args.database]

    conn = f"postgresql://{db_access['host']}/{args.database}?user={db_access['username']}&password={db_access['password']}"

    with open(args.sample_tax_map, "rt", encoding="UTF-8") as _in:
        st_map = dict(line.strip().split("\t")[::-1] for line in _in)
    with open(args.bulk_file, "rt", encoding="UTF-8") as _in:
        query_list = [(st_map.get(".".join(line.strip().split("/")[1].split(".")[:-1])), line.strip()) for line in _in]
    query_list_str = ", ".join(f"'{pid}'" for pid, _ in query_list if pid is not None)
    query = f"SELECT * from eggnog WHERE project_id IN ({query_list_str});"

    st_map = {v: k for k, v in st_map.items()}
    p_map = dict(query_list)
    eggnog = pd.read_sql(query, conn)
    annotated_genomes = []
    print(query_list[:10])
    for pid in eggnog["project_id"].unique():
        print(pid)
        genome_id = st_map.get(pid)
        annotated_genomes.append(genome_id)
        eggnog[eggnog["project_id"] == pid].drop("project_id", axis=1).to_csv(
            os.path.join(p_map.get(pid), f"{genome_id.split('/')[0]}.emapper_annotations"),
            sep="\t",
            header=DbEmapperResult.HEADERS,
            index=False,
        )

    if args.fill_missing:
        # write empty emapper annotations
        # for rare cases where we neither have db records
        # nor annotations on the file system
        # genome will not have cargo/phage annotation
        # but could still contain e.g. recombinase signals
        for genome_id in set(v for _, v in query_list).difference(annotated_genomes):
            path = pathlib.Path(genome_id)
            path.mkdir(parents=True, exist_ok=True)
            (path / f"{genome_id.split('/')[1]}.emapper_annotations").touch()



if __name__ == "__main__":
    main()
