# -*- coding: utf-8 -*-
import json
import logging
from pprint import pprint as pp

import click
from pymongo.cursor import Cursor

from loqusdb.commands.cli import cli as base_command
from loqusdb.utils.variant import normalize_mei_type

LOG = logging.getLogger(__name__)


@base_command.command("cases", short_help="Display cases in database")
@click.option("-c", "--case-id", help="Search for case")
@click.option("--to-json", is_flag=True)
@click.option("--count", is_flag=True, help="Show number of cases in database")
@click.option(
    "--case-type", "-t", help="Specify the type of cases", type=click.Choice(["snv", "sv", "mei"])
)
@click.pass_context
def cases(ctx, case_id, to_json, count, case_type):
    """Display cases in the database."""

    adapter = ctx.obj["adapter"]
    cases = []

    if count:
        click.echo(
            adapter.nr_cases(
                snv_cases=case_type == "snv",
                sv_cases=case_type == "sv",
                mei_cases=case_type == "mei",
            )
        )
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
        vcf_path = (
            case_obj.get("vcf_path") or case_obj.get("vcf_sv_path") or case_obj.get("vcf_mei_path")
        )
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
    type=click.Choice(["sv", "snv", "mei"]),
    default="snv",
)
@click.option(
    "--sv-type",
    help="Type of svs to search for. For meis, the element type e.g. ALU or INS:ME:ALU",
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
    if sv_type and variant_type == "snv":
        variant_type = "sv"
    if variant_type == "mei" and sv_type:
        sv_type = normalize_mei_type(sv_type)

    adapter = ctx.obj["adapter"]
    variant = {}
    if start or end:
        if not (chromosome and start and end):
            LOG.warning("Regions must be specified with chromosome, start and end")
            return

    nr_cases = None
    if case_count:
        nr_cases = adapter.nr_cases(
            snv_cases=variant_type == "snv",
            sv_cases=variant_type == "sv",
            mei_cases=variant_type == "mei",
        )

    chromosomes = [None, None]
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
        if variant_type in ["sv", "mei"]:
            if not (chromosome and start):
                LOG.warning("SV and MEI variants must be searched with chromosome and start")
                return
            get_cluster = (
                adapter.get_mei_variant if variant_type == "mei" else adapter.get_structural_variant
            )
            variant = None
            for chrom, end_chrom in zip(chromosomes, end_chromosomes):
                variant_query = {
                    "chrom": chrom,
                    "end_chrom": end_chrom or chrom,
                    "sv_type": sv_type,
                    "pos": start,
                    # MEIs are point events
                    "end": start if variant_type == "mei" else end,
                }
                variant = get_cluster(variant_query)
                if variant:
                    break
            variant = variant or {}

        else:
            variant = adapter.get_variant({"_id": variant_id})

        if not variant:
            LOG.info("Variant {0} does not exist in database".format(variant_id))
            variant = {}

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
    elif variant_type == "mei":
        LOG.info("Search for meis")
        result = []
        for chrom in dict.fromkeys(chromosomes):
            result = list(
                adapter.get_mei_variants(chromosome=chrom, sv_type=sv_type, pos=start, end=end)
            )
            if result:
                break
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
