# pylint: disable=W2301,R0903,E1101,C0103

""" Functions for database access. """

import json
import random
import time

from functools import lru_cache

from sqlalchemy import create_engine, MetaData, Table
from sqlalchemy.orm import mapper, sessionmaker, registry
from sqlalchemy.exc import OperationalError


class DbGene:
    """ Placeholder Gene class"""
    ...


class DbGeneCluster:
    """ Placeholder GeneCluster class"""
    ...


class DbEmapperResult:
    """ Emapper results class"""
    HEADERS = [
        "#query",
        "seed_ortholog",
        "evalue",
        "score",
        "eggNOG_OGs",
        "max_annot_lvl",
        "COG_category",
        "Description",
        "Preferred_name",
        "GOs",
        "EC",
        "KEGG_ko",
        "KEGG_Pathway",
        "KEGG_Module",
        "KEGG_Reaction",
        "KEGG_rclass",
        "BRITE",
        "KEGG_TC",
        "CAZy",
        "BiGG_Reaction",
    ]

    def __str__(self):
        """ String representation. """
        return "\t".join(str(v) for k, v in self.__dict__.items() if k != "project_id")


def read_db_details(f):
    """ Reads database credentials from JSON file. """
    with open(f, "rt", encoding="UTF-8") as _in:
        return json.load(_in)


@lru_cache(maxsize=10000)
def get_cluster(db_session, cluster_id):
    """ Queries GeneCluster table by cluster_id. """
    cluster = (
        db_session.query(DbGeneCluster).filter(DbGeneCluster.id == cluster_id).one_or_none()
    )
    return cluster


def get_gene(db_session, gene_id):
    """ Queries Gene table by gene_id. """
    gene = (
        db_session.query(DbGene).filter(DbGene.id == gene_id).one_or_none()
    )
    return gene


def db_available(cluster_id):
    """ Checks if cluster data is stored in db.
    (Only the largest 10 clusters are.)
    """
    return int(cluster_id.replace("specI_v4_", "")) in range(9)


def initialise_db(db_details, db_name, cluster_id=""):
    """ Initialises database connection. """

    db_access = read_db_details(db_details)[db_name]

    engine = create_engine(
        f"postgresql+psycopg2://{db_access['username']}:"
        f"{db_access['password']}@{db_access['host']}/{db_name}"
    )

    metadata = MetaData()

    if cluster_id.lower() == "speci_v4_00000":
        cluster_id = ""

    # strips "_" in case of specI_v4_00000
    gene_table_name = f"{cluster_id}_gene".strip("_")
    gene_cluster_table_name = f"{cluster_id}_gene_cluster".strip("_")

    while 1:
        try:
            gene_table = Table(
                gene_table_name,
                metadata,
                autoload_with=engine
            )

            gene_cluster_table = Table(
                gene_cluster_table_name,
                metadata,
                autoload_with=engine
            )

            # [mapper(DbGene, gene_table), mapper(DbGeneCluster, gene_cluster_table)]
            mapper_registry = registry()
            mapper_registry.map_imperatively(DbGene, gene_table)
            mapper_registry.map_imperatively(DbGeneCluster, gene_cluster_table)

            Session = sessionmaker(bind=engine)
            session = Session()
        except OperationalError:
            time.sleep(random.randint(1, 31))
        else:
            break

    return session


def initialise_pg3_db(db_details, db_name):
    """ Initialises connection to PG3 database for emapper queries. """
    db_access = read_db_details(db_details)[db_name]

    engine = create_engine(
        f"postgresql+psycopg2://{db_access['username']}:"
        f"{db_access['password']}@{db_access['host']}/{db_name}"
    )

    metadata = MetaData(engine)

    emapper_table = Table(
        "eggnog",
        metadata,
        autoload=True
    )

    mapper(DbEmapperResult, emapper_table)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session
