# -*- coding: utf-8 -*-
import logging

from loqusdb.vcf_tools import get_formated_variant

logger = logging.getLogger(__name__)


def delete_variants(adapter, variant_stream, family_id, affected_individuals):
    case = {'case_id': family_id}
    adapter.delete_case(case)

    header = []
    nr_of_deleted = 0
    for line in variant_stream:
        line = line.rstrip()
        if line.startswith('#'):
            if not line.startswith('##'):
                header = line[1:].split()
        else:
            formated_variant = get_formated_variant(
                variant_line=line, header_line=header,
                affected_individuals=affected_individuals)

            adapter.delete_variant(formated_variant)
            nr_of_deleted += 1

    return nr_of_deleted
