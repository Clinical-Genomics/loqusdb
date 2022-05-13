#!/usr/bin/python
# -*- coding: utf-8 -*-
import re

import click

from pymongo import MongoClient

@click.command()
@click.option("--db-uri", required=True, help="mongodb://user:password@db_url:db_port")
@click.option("--db-name", required=True, help="db name")
@click.option("--live", help="Use this flag to arm the script", is_flag=True, default=False)
def revert_contig_name_trim(db_uri, db_name, live=False):
    try:
        client = MongoClient(db_uri)
        db = client[db_name]
        # test connection
        click.echo("database connection info:{}".format(db))
        old_GL_pattern = re.compile("^L00")

        variants = list(db.structural_variant.find(
            {"end_chrom": old_GL_pattern}))

        click.echo(f"found: {len(variants)} trimmed end_chrom")

        for variant in variants:
            old_end = variant["end_chrom"]
            new_end = "G" + old_end
            variant["end_chrom"] = new_end
            if live:
                db.structural_variant.find_one_and_update(
                    {"_id": variant["_id"]}, {"$set": {"end_chrom": new_end}}
                )
            click.echo(f"old end_chrom: {old_end} -> new end_chrom {new_end}")

    except Exception as err:
        click.echo("Error {}".format(err))

if __name__ == "__main__":
    revert_contig_name_trim()
