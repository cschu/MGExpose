#!/usr/bin/env python

""" Module for processing mmseqs2 linclust output. """

import argparse
import gzip
import os
import warnings

from db import initialise_db, db_available, get_gene, get_cluster
from readers import read_prodigal_gff


def main():
    """ maaaaaaain... """
    ap = argparse.ArgumentParser()
    ap.add_argument("genome_id", type=str)
    ap.add_argument("speci", type=str)
    ap.add_argument("prodigal_gff", type=str)
    ap.add_argument("--cluster_db_credentials", type=str)
    ap.add_argument("--output_dir", "-o", type=str, default=".")
    ap.add_argument("--dump_intermediate_steps", action="store_true")

    args = ap.parse_args()

    db_session = None
    if args.cluster_db_credentials:
        if db_available(args.speci):
            db_session = initialise_db(
                args.cluster_db_credentials,
                "mge_clusters",
                cluster_id=args.speci.lower(),
            )
        else:
            warnings.warn(
                "Could not connect to database.\n"
                f"Check if {args.speci} database exists in specified "
                f"database ({args.cluster_db_credentials}.)"
            )
            return None

        print("DB_SESSION", db_session is not None)

        gene_clusters_out = gzip.open(
            os.path.join(args.output_dir, f"{args.genome_id}.db_gene_clusters.txt.gz"),
            "wt",
        )

        with gene_clusters_out:
            for gene_id, _ in read_prodigal_gff(args.prodigal_gff):
                db_gene = get_gene(db_session, gene_id)
                if db_gene is not None:
                    db_cluster = get_cluster(db_session, db_gene.cluster_id)
                    if db_cluster is not None:
                        print(
                            gene_id,
                            db_cluster.name,
                            db_gene.is_core,
                            sep="\t",
                            file=gene_clusters_out,
                        )

    return None


if __name__ == "__main__":
    main()
