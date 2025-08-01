#!/usr/bin/env python
# pylint: disable=E0401,C0415,R0914,W0702,W0621,W0404,C0301
# flake8: noqa

""" Functions to load speci cluster data from cache/seq repo. """

import argparse
import gzip
import json
import os

import pymongo


def get_sequences_from_cluster(mongo_db_str, cluster_id, seqfile):
    """ Get cluster sequences from cache/seq repo """

    try:
        import pymongo
    except ImportError:
        return 0

    client = pymongo.MongoClient(mongo_db_str,)
    fr_db = client["progenomes"]

    n_genes = 0
    files = []
    with gzip.open(seqfile, "wt") as genes_out:
        for record in fr_db.samples.find({'fr13_cluster': cluster_id}):
            genes_file = f"{record['analysis_path']}/ref_genome_called_genes/{record['sample_id']}.genes.fa.gz"
            files.append(genes_file)
        for genes_file in files:
            with gzip.open(genes_file, "rt") as genes_in:
                genes_raw = genes_in.read()
                n_genes += genes_raw.count(">")
                print(genes_raw, file=genes_out, end="" if genes_raw[-1] == "\n" else "\n")

    return n_genes


def main():
    """ Main. """

    ap = argparse.ArgumentParser()
    ap.add_argument("dbname", type=str)
    ap.add_argument("dbcred", type=str)
    ap.add_argument("cluster_id", type=str)
    ap.add_argument("outfile", type=str)
    ap.add_argument("outfile_ids", type=str)
    ap.add_argument("--cache", type=str)
    args = ap.parse_args()

    try:
        with open(args.dbcred, "rt", encoding="UTF-8") as _in:
            db_d = json.load(_in).get(args.dbname)
    except:
        db_d = {}

    user = db_d.get("username")
    host = db_d.get("host")
    pw = db_d.get("password")
    port = db_d.get("port")

    dbstr = f"mongodb://{user}:{pw}@{host}:{port}" if (user and host and pw and port) else None

    client = pymongo.MongoClient(dbstr,)
    fr_db = client["progenomes"]

    n_genes = 0
    files = []

    n_seqs = 0
    if args.cache and os.path.isdir(args.cache):
        print("Looking up seq_cache...")
        expected_files = [
            os.path.join(args.cache, f"{args.cluster_id}.{suffix}")
            for suffix in ("genes.ffn.gz", "genes.nseqs", "genes.ids.gz")
        ]
        if all(os.path.isfile(f) and os.stat(f).st_size for f in expected_files):
            with open(os.path.join(args.cache, f"{args.cluster_id}.genes.nseqs"), "rt", encoding="UTF-8") as _in:
                n_seqs = int(_in.read().strip())
            print("Copying sequences from seq_cache:", args.cluster_id, args.outfile, "...", end="")
            # shutil.copyfile(os.path.join(args.cache, f"{args.cluster_id}.genes.ffn.gz"), args.outfile)

            os.symlink(os.path.join(args.cache, f"{args.cluster_id}.genes.ffn.gz"), args.outfile)
            os.symlink(os.path.join(args.cache, f"{args.cluster_id}.genes.ids.gz"), args.outfile_ids)
            print(n_seqs)

    if not n_seqs:
        with gzip.open(args.outfile, "wt") as genes_out, gzip.open(args.outfile_ids, "wt") as geneids_out:
            for record in fr_db.samples.find({'fr13_cluster': args.cluster_id}):
                genes_file = f"{record['analysis_path']}/ref_genome_called_genes/{record['sample_id']}.genes.fa.gz"
                files.append(genes_file)
            for genes_file in files:
                with gzip.open(genes_file, "rt") as genes_in:
                    genes_raw = genes_in.read()
                    n_genes += genes_raw.count(">")
                    print(genes_raw, file=genes_out, end="" if genes_raw[-1] == "\n" else "\n")

                    genes_raw = (
                        line[1:].split(" ")[0]
                        for line in genes_raw.strip().split("\n")
                        if line[0] == ">"
                    )
                    print(*genes_raw, file=geneids_out, sep="\n")


if __name__ == "__main__":
    main()
