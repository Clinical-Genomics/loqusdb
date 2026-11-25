# -*- coding: utf-8 -*-
import json
import logging
from pprint import pprint as pp

import click
from pymongo.cursor import Cursor

from loqusdb.commands.cli import cli as base_command

LOG = logging.getLogger(__name__)


@base_command.command("cases", short_help="Display cases in database")
@click.option("-c", "--case-id", help="Search for case")
@click.option("--to-json", is_flag=True)
@click.option("--count", is_flag=True, help="Show number of cases in database")
@click.option(
    "--case-type", "-t", help="Specify the type of cases", type=click.Choice(["snv", "sv"])
)
@click.pass_context
def cases(ctx, case_id, to_json, count, case_type):
    """Display cases in the database."""

    adapter = ctx.obj["adapter"]
    cases = []

    if count:
        snv_cases = None
        sv_cases = None
        if case_type == "snv":
            snv_cases = True
        elif case_type == "sv":
            sv_cases = True
        click.echo(adapter.nr_cases(snv_cases=snv_cases, sv_cases=sv_cases))
        return

    if case_id:
        case_obj = adapter.case({"case_id": case_id})
        if not case_obj:
            LOG.info("Case {0} does not exist in database".format(case_id))
            return
        case_obj["_id"] = str(case_obj["_id"])
        cases.append(case_obj)
    else:
        case_count: int = adapter.case_count()
        if case_count == 0:
            LOG.info("No cases found in database")
            ctx.abort()
        cases: Cursor = adapter.cases()

    if to_json:
        click.echo(json.dumps(cases))
        return

    click.echo("#case_id\tvcf_path")

    for case_obj in cases:
        case_id = case_obj.get("case_id")
        vcf_path = case_obj.get("vcf_path", case_obj.get("vcf_sv_path"))
        click.echo("{0}\t{1}".format(case_id, vcf_path))


@base_command.command("variants", short_help="Display variants in database")
@click.option("--variant-id", help="Search for a variant")
@click.option("-c", "--chromosome", help="Search for all variants in a chromosome")
@click.option("--end-chromosome", help="Search for all variants that ends on chromosome")
@click.option("-s", "--start", help="Start of region", type=int)
@click.option("-e", "--end", help="End of region", type=int)
@click.option(
    "-t",
    "--variant-type",
    help="Variant type to search for",
    type=click.Choice(["sv", "snv"]),
    default="snv",
)
@click.option(
    "--sv-type",
    help="Type of svs to search for",
)
@click.option("--to-json", is_flag=True)
@click.option("--case-count", is_flag=True, help="If number of cases should be included")
# @click.option('--sort-key',
#                 help='Specify what field to sort on',
# )
@click.pass_context
def variants(
    ctx,
    variant_id,
    chromosome,
    end_chromosome,
    start,
    end,
    variant_type,
    sv_type,
    to_json,
    case_count,
):
    """Display variants in the database."""
    if sv_type:
        variant_type = "sv"

    adapter = ctx.obj["adapter"]
    variant = {}
    if start or end:
        if not (chromosome and start and end):
            LOG.warning("Regions must be specified with chromosome, start and end")
            return

    nr_cases = None
    if case_count:
        snv_cases = None
        sv_cases = None
        if variant_type == "snv":
            snv_cases = True
        if variant_type == "sv":
            sv_cases = True
        nr_cases = adapter.nr_cases(snv_cases=snv_cases, sv_cases=sv_cases)

    if chromosome:
        if chromosome.startswith("chr"):
            chromosomes = [chromosome, chromosome[3:]]
        elif not chromosome.startswith("chr"):
            chromosomes = [chromosome, "chr" + chromosome]

    if end_chromosome:
        if end_chromosome.startswith("chr"):
            end_chromosomes = [end_chromosome, end_chromosome[3:]]
        elif not end_chromosome.startswith("chr"):
            end_chromosomes = [end_chromosome, "chr" + end_chromosome]
    else:
        end_chromosomes = [None, None]

    if variant_id:
        if variant_type == "sv":
            variant_query = {
                "chrom": chromosomes[0],
                "end_chrom": end_chromosomes[0] or chromosomes[0],
                "sv_type": sv_type,
                "pos": start,
                "end": end,
            }
            variant = list(adapter.get_structural_variant(variant_query))
            if len(variant) == 0:
                variant_query = {
                    "chrom": chromosomes[1],
                    "end_chrom": end_chromosomes[1] or chromosomes[1],
                    "sv_type": sv_type,
                    "pos": start,
                    "end": end,
                }
                variant = adapter.get_structural_variant(variant_query)

        else:
            variant = adapter.get_variant({"_id": variant_id})

        if not variant:
            LOG.info("Variant {0} does not exist in database".format(variant_id))

        if case_count:
            variant["total"] = nr_cases

        if to_json:
            LOG.info("Print in json format")
            if "_id" in variant:
                variant.pop("_id")
            click.echo(json.dumps(variant))
            return

        click.echo(variant)
        return
    if variant_type == "snv":
        result = list(adapter.get_variants(chromosome=chromosomes[0], start=start, end=end))
        if len(result) == 0:
            result = adapter.get_variants(chromosome=chromosomes[1], start=start, end=end)
    else:
        LOG.info("Search for svs")
        result = list(
            adapter.get_sv_variants(
                chromosome=chromosomes[0],
                end_chromosome=end_chromosomes[0],
                sv_type=sv_type,
                pos=start,
                end=end,
            )
        )
        if len(result) == 0:
            result = adapter.get_sv_variants(
                chromosome=chromosomes[1],
                end_chromosome=end_chromosomes[1],
                sv_type=sv_type,
                pos=start,
                end=end,
            )

    if to_json:
        json.dumps(variant)

    i = 0
    for i, variant in enumerate(result, 1):
        pp(variant)

    LOG.info("Number of variants found in database: %s", i)


@base_command.command("index", short_help="Add indexes to database")
@click.option(
    "--view",
    is_flag=True,
    help="Only display existing indexes",
)
@click.pass_context
def index(ctx, view):
    """Index the database."""
    adapter = ctx.obj["adapter"]
    if view:
        click.echo(adapter.indexes())
        return
    adapter.ensure_indexes()
