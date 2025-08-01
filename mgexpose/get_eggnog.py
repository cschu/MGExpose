#!/usr/bin/env python
# pylint: disable=C0301
# flake8: noqa

""" Get emapper data from database. """

import argparse

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

    args = ap.parse_args()

    db_access = read_db_details(args.credentials)[args.database]

    conn = f"postgresql://{db_access['host']}/{args.database}?user={db_access['username']}&password={db_access['password']}"

    if args.bulk_file:
        with open(args.bulk_file, "rt", encoding="UTF-8") as _in:
            query_list = [line.strip() for line in _in]
        query_list_str = ", ".join(line for line in query_list)
        query = f"SELECT * from eggnog WHERE project_id IN ({query_list_str});"
    else:
        column, column_value = ("project_id", args.project_id) if args.project_id else ("sample_name", args.sample_name)
        query = f"SELECT * from eggnog WHERE {column} = '{column_value}';"

    eggnog = pd.read_sql(query, conn)
    try:
        eggnog = eggnog.drop("project_id", axis=1)
    except KeyError:
        pass
    try:
        eggnog = eggnog.drop(["sample_name", "contig_name", "pfams",], axis=1)
    except KeyError:
        pass
    eggnog.columns = DbEmapperResult.HEADERS
    eggnog.to_csv("emapper.annotations", sep="\t", index=False)


if __name__ == "__main__":
    main()
