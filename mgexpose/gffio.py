""" GFF I/O -- wannabe serialisation module """

from gene import Gene
from islands import GenomicIsland


def read_genomic_islands_gff(fn):
    """ reads a set of genomic islands + genes from a gff3 """
    with open(fn, "rt", encoding="UTF-8") as _in:
        island = None
        for line in _in:
            line = line.strip()
            if line and line[0] != "#":
                cols = line.split("\t")
                if cols[2] == "region":
                    if island is not None:
                        yield island
                    island = GenomicIsland.from_gff(*cols)
                elif cols[2] == "gene":
                    gene = Gene.from_gff(*cols)
                    if island is not None:
                        island.genes.add(gene)
                    else:
                        raise ValueError("Found gene but no island.")
        if island is not None:
            yield island
