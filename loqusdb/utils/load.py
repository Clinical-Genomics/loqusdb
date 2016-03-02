# -*- coding: utf-8 -*-
from datetime import datetime
import logging

from loqusdb.vcf_tools import get_formated_variant

logger = logging.getLogger(__name__)


def load_variants(adapter, family_id, affected_individuals, variant_stream,
                  bulk_insert=False, vcf_path=None):
    """Load variants for a family into the database.

    Args:
        adapter (loqusdb.plugins.MongoAdapter): initialized plugin
        family_id (str): unique family identifier
        affected_inidividuals (List[str]): list to match individuals
        variant_stream (sequence): stream of VCF lines
        bulk_insert (bool): whether to insert in bulk or one-by-one
        vcf_path (path): for storing in database
    """
    case = {'case_id': family_id, 'vcf_path': vcf_path}
    adapter.add_case(case)

    # This is the header line with mandatory vcf fields
    header = []
    nr_of_variants = 0
    nr_of_inserted = 0

    start_inserting = datetime.now()
    start_ten_thousand = datetime.now()

    variants = []
    for line in variant_stream:
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
