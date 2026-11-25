from loqusdb.constants import GRCH37, MEI_COLLECTION, SV_COLLECTION
from loqusdb.utils.annotate import annotate_meis
from loqusdb.utils.delete import delete
from loqusdb.utils.load import load_database
from loqusdb.utils.update import update_database
from loqusdb.utils.variant import format_variant
from loqusdb.utils.vcf import add_headers, get_vcf

NR_MEIS = 18


def _load_meis(adapter, mei_vcf_path, ped_path, **kwargs):
    return load_database(
        adapter=adapter,
        mei_file=mei_vcf_path,
        family_file=ped_path,
        genome_build=GRCH37,
        **kwargs,
    )


def test_load_mei_database(mongo_adapter, mei_vcf_path, ped_path, case_id):
    ## GIVEN an empty database
    ## WHEN loading a MEI VCF for a case
    nr_inserted = _load_meis(mongo_adapter, mei_vcf_path, ped_path)
    ## THEN all MEIs are inserted into the mei collection
    assert nr_inserted == NR_MEIS
    assert mongo_adapter.db[MEI_COLLECTION].count_documents({}) == NR_MEIS
    assert mongo_adapter.db[SV_COLLECTION].count_documents({}) == 0
    assert mongo_adapter.db.variant.count_documents({}) == 0
    assert set(mongo_adapter.get_mei_types()) == {"INS:ME:ALU", "INS:ME:L1"}
    ## THEN the case knows about the MEI file and its individuals
    case_obj = mongo_adapter.case({"case_id": case_id})
    assert case_obj["vcf_mei_path"] == mei_vcf_path
    assert case_obj["nr_mei_variants"] == NR_MEIS
    assert len(case_obj["mei_individuals"]) == 3
    assert case_obj["individuals"] == []
    assert mongo_adapter.nr_cases(mei_cases=True) == 1
    assert mongo_adapter.nr_cases(sv_cases=True) == 0


def test_load_mei_database_twice_merges(mongo_adapter, mei_vcf_path, ped_path):
    ## GIVEN a database with MEIs from one case
    _load_meis(mongo_adapter, mei_vcf_path, ped_path)
    ## WHEN loading the same MEIs for another case
    _load_meis(mongo_adapter, mei_vcf_path, ped_path, case_id="other_case")
    ## THEN the clusters are shared
    assert mongo_adapter.db[MEI_COLLECTION].count_documents({}) == NR_MEIS
    for cluster in mongo_adapter.db[MEI_COLLECTION].find():
        assert cluster["observations"] == 2


def test_load_snv_sv_and_mei(
    real_mongo_adapter, vcf_path, sv_vcf_path, mei_vcf_path, ped_path, case_id
):
    ## WHEN loading all three variant types at once
    load_database(
        adapter=real_mongo_adapter,
        variant_file=vcf_path,
        sv_file=sv_vcf_path,
        mei_file=mei_vcf_path,
        family_file=ped_path,
        genome_build=GRCH37,
        gq_threshold=20,
    )
    ## THEN all collections are populated, and the case has all individuals
    assert real_mongo_adapter.db[MEI_COLLECTION].count_documents({}) == NR_MEIS
    assert real_mongo_adapter.db[SV_COLLECTION].count_documents({}) > 0
    assert real_mongo_adapter.db.variant.count_documents({}) > 0
    case_obj = real_mongo_adapter.case({"case_id": case_id})
    assert len(case_obj["individuals"]) == len(case_obj["mei_individuals"]) == 3


def test_delete_mei_case(mongo_adapter, mei_vcf_path, ped_path, case_id):
    ## GIVEN a database with MEIs from a case
    _load_meis(mongo_adapter, mei_vcf_path, ped_path)
    ## WHEN deleting the case
    delete(
        adapter=mongo_adapter,
        case_obj=mongo_adapter.case({"case_id": case_id}),
        genome_build=GRCH37,
    )
    ## THEN the case and its MEIs are gone
    assert mongo_adapter.case({"case_id": case_id}) is None
    assert mongo_adapter.db[MEI_COLLECTION].count_documents({}) == 0


def test_update_case_with_meis(real_mongo_adapter, vcf_path, mei_vcf_path, ped_path, case_id):
    ## GIVEN a case with SNVs
    load_database(
        adapter=real_mongo_adapter,
        variant_file=vcf_path,
        family_file=ped_path,
        genome_build=GRCH37,
        gq_threshold=20,
    )
    snv_observations = sum(v["observations"] for v in real_mongo_adapter.db.variant.find())
    ## WHEN updating the case with MEIs
    nr_inserted = update_database(
        adapter=real_mongo_adapter,
        mei_file=mei_vcf_path,
        family_file=ped_path,
        genome_build=GRCH37,
    )
    ## THEN the MEIs are added, and the SNVs are not loaded again
    assert nr_inserted == NR_MEIS
    assert real_mongo_adapter.db[MEI_COLLECTION].count_documents({}) == NR_MEIS
    assert sum(v["observations"] for v in real_mongo_adapter.db.variant.find()) == snv_observations
    case_obj = real_mongo_adapter.case({"case_id": case_id})
    assert case_obj["vcf_path"] == vcf_path
    assert case_obj["vcf_mei_path"] == mei_vcf_path


def test_format_mei_variant(mongo_adapter, mei_vcf_path, ped_path):
    ## GIVEN a database with MEIs
    _load_meis(mongo_adapter, mei_vcf_path, ped_path)
    cluster = next(iter(mongo_adapter.get_mei_variants(chromosome="1")))
    ## WHEN formatting a cluster for export
    line = format_variant(cluster, variant_type="mei", nr_cases=1, add_freq=True)
    chrom, pos, _, ref, alt, _, _, info = line.split("\t")
    ## THEN it is a generic mobile element insertion, with the element in MEINFO
    assert (chrom, pos, ref, alt) == ("1", "21898411", "N", "<INS:ME>")
    assert info == "Obs=1;Frq=1.00000;SVTYPE=INS;MEINFO=ALU,.,.,."


def test_annotate_meis(mongo_adapter, mei_vcf_path, ped_path):
    ## GIVEN a database with MEIs from a case
    _load_meis(mongo_adapter, mei_vcf_path, ped_path)
    ## WHEN annotating the same VCF
    vcf_obj = get_vcf(mei_vcf_path)
    add_headers(vcf_obj, sv=True)
    annotated = list(annotate_meis(mongo_adapter, vcf_obj, keep_chr_prefix=False))
    ## THEN all MEIs are annotated with their observations
    assert len(annotated) == NR_MEIS
    assert all(variant.INFO.get("Obs") == 1 for variant in annotated)
