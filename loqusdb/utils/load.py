# -*- coding: utf-8 -*-
from datetime import datetime
import logging
import sys

from vcftoolbox import get_vcf_handle

from loqusdb.vcf_tools import get_formated_variant

logger = logging.getLogger(__name__)


def load_variants(adapter, family_id, affected_individuals, variant_file,
                  bulk_insert=False, family_type='ped'):
    """Load variants for a family into the database."""
    case = {'case_id': family_id, 'vcf_path': variant_file}
    adapter.add_case(case)

    if variant_file == '-':
        logger.info("Parsing variants from stdin")
        variant_file = get_vcf_handle(fsock=sys.stdin)
    else:
        logger.info("Start parsing variants from stdin")
        variant_file = get_vcf_handle(infile=variant_file)

    # This is the header line with mandatory vcf fields
    header = []
    nr_of_variants = 0
    nr_of_inserted = 0

    start_inserting = datetime.now()
    start_ten_thousand = datetime.now()

    variants = []
    for line in variant_file:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split()
        else:
            nr_of_variants += 1

            formated_variant = get_formated_variant(
                variant_line=line, header_line=header,
                affected_individuals=affected_individuals)

            if formated_variant:
                nr_of_inserted += 1
                if bulk_insert:
                    variants.append(formated_variant)
                else:
                    adapter.add_variant(variant=formated_variant)

            if nr_of_variants % 10000 == 0:
                logger.info("{0} of variants processed".format(nr_of_variants))
                logger.info("Time to insert last 10000: {0}".format(
                    datetime.now()-start_ten_thousand))
                start_ten_thousand = datetime.now()

            if nr_of_variants % 100000 == 0:
                if bulk_insert:
                    adapter.add_bulk(variants)
                    variants = []

    if bulk_insert:
        adapter.add_bulk(variants)

    logger.info("Nr of variants in vcf: {0}".format(nr_of_variants))
    logger.info("Nr of variants inserted: {0}".format(nr_of_inserted))
    logger.info("Time to insert variants: {0}".format(datetime.now() -
                                                      start_inserting))
