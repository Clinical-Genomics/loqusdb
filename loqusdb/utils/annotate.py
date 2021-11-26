"""
loqusdb/utils/annotate.py

Functions to annotate variants in a VCF

The methods for annotating SNVs and SVs differs a bit so they will be handeld in separate.

"""

from loqusdb.build_models.variant import get_coords, get_variant_id


def annotate_variant(variant, var_obj=None):
    """Annotate a cyvcf variant with observations

    Args:
        variant(cyvcf2.variant)
        var_obj(dict)

    Returns:
        variant(cyvcf2.variant): Annotated variant
    """
    if var_obj:

        variant.INFO["Obs"] = var_obj["observations"]
        if var_obj.get("homozygote"):
            variant.INFO["Hom"] = var_obj["homozygote"]
        if var_obj.get("hemizygote"):
            variant.INFO["Hem"] = var_obj["hemizygote"]

    return variant


def annotate_snv(adpter, variant):
    """Annotate an SNV/INDEL variant

    Args:
        adapter(loqusdb.plugin.adapter)
        variant(cyvcf2.Variant)
    """
    variant_id = get_variant_id(variant)
    variant_obj = adapter.get_variant(variant={"_id": variant_id})

    annotated_variant = annotated_variant(variant, variant_obj)
    return annotated_variant


def annotate_svs(adapter, vcf_obj):
    """Annotate all SV variants in a VCF

    Args:
        adapter(loqusdb.plugin.adapter)
        vcf_obj(cyvcf2.VCF)

    Yields:
        variant(cyvcf2.Variant)
    """
    for nr_variants, variant in enumerate(vcf_obj, 1):
        variant_info = get_coords(variant)
        match = adapter.get_structural_variant(variant_info)
        if match:
            annotate_variant(variant, match)
        yield variant


def annotate_snvs(adapter, vcf_obj):
    """Annotate all variants in a VCF

    Args:
        adapter(loqusdb.plugin.adapter)
        vcf_obj(cyvcf2.VCF)

    Yields:
        variant(cyvcf2.Variant): Annotated variant
    """
    variants = {}

    for nr_variants, variant in enumerate(vcf_obj, 1):
        # Add the variant to current batch
        variants[get_variant_id(variant)] = variant
        # If batch len == 1000 we annotate the batch
        if (nr_variants % 1000) == 0:

            for var_obj in adapter.search_variants(list(variants.keys())):
                var_id = var_obj["_id"]
                if var_id in variants:
                    annotate_variant(variants[var_id], var_obj)

            for variant_id in variants:
                yield variants[variant_id]

            variants = {}

    for var_obj in adapter.search_variants(list(variants.keys())):
        var_id = var_obj["_id"]
        if var_id in variants:
            annotate_variant(variants[var_id], var_obj)

    for variant_id in variants:
        yield variants[variant_id]
