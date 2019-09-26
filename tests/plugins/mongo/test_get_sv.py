from loqusdb.build_models.variant import build_variant
from loqusdb.plugins.mongo.structural_variant import HARD_LIMIT_ACCURACY

def test_get_insertion(small_insert_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a small insertion
    variant = small_insert_variant
    case_id = case_obj['case_id']
    formated_variant = build_variant(
        variant=variant,
        case_obj=case_obj,
        case_id=case_id
    )
    
    adapter.add_case(case_obj)
    adapter.add_structural_variant(formated_variant)
    for variant_obj in adapter.db.structural_variant.find():
        assert variant_obj

def test_get_translocation(translocation_variant, mongo_adapter, case_obj):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a translocation
    variant = translocation_variant
    case_id = case_obj['case_id']
    formated_variant = build_variant(
        variant=variant,
        case_obj=case_obj,
        case_id=case_id
    )
    
    adapter.add_case(case_obj)
    adapter.add_structural_variant(formated_variant)
    for variant_obj in adapter.db.structural_variant.find():
        assert variant_obj

def test_count_borderline_cases(small_insert_variant, insertion_variant_inaccurate, insertion_variant_accurate, mongo_adapter, sv_case_obj, sv_case_obj2):
    adapter = mongo_adapter
    ## GIVEN a mongo adapter with a small insertion (listed twice in VCF), one insertion larger than 100bp (inaccurate, i.e. not sequence resolved)
    ## AND and one insertion larger than 100p from another family (similar to the larger variant from first family, but accurate, i.e. sequence resolved)
    variant_smaller = small_insert_variant
    variant_larger_inaccurate = insertion_variant_inaccurate
    variant_larger_accurate = insertion_variant_accurate
    sv_case_id = sv_case_obj['case_id']
    sv_case_id2 = sv_case_obj2['case_id']
    
    formated_variant_smaller = build_variant(
        variant=variant_smaller,
        case_obj=sv_case_obj,
        case_id=sv_case_id
    )
    formated_variant_smaller_duplicate = build_variant(
        variant=variant_smaller,
        case_obj=sv_case_obj,
        case_id=sv_case_id
    )
    formated_variant_larger_inaccurate = build_variant(
        variant=variant_larger_inaccurate,
        case_obj=sv_case_obj,
        case_id=sv_case_id
    )
    formated_variant_larger_accurate = build_variant(
        variant=variant_larger_accurate,
        case_obj=sv_case_obj2,
        case_id=sv_case_id2
    )
    
    adapter.add_case(sv_case_obj)
    adapter.add_case(sv_case_obj2)
    adapter.add_structural_variant(formated_variant_larger_accurate)
    adapter.add_structural_variant(formated_variant_larger_inaccurate)
    adapter.add_structural_variant(formated_variant_smaller)
    adapter.add_structural_variant(formated_variant_smaller_duplicate)

    # Test is written for the case that variants less than 100bp are considered accurate
    assert HARD_LIMIT_ACCURACY == 100

    for variant in [formated_variant_larger_inaccurate, formated_variant_smaller, formated_variant_larger_accurate, formated_variant_smaller_duplicate]:
        var = adapter.get_structural_variant(variant)
        # Variants larger than 100bp are not clustered together with variants smaller than 100bp
        if var["length"] >= 100:
            # Variants from different families are added
            assert var["observations"] == 2
        else:
            # Duplicate is not added to cluster
            assert var["observations"] == 1
