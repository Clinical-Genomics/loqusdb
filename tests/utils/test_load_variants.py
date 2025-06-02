from cyvcf2 import VCF

from loqusdb.utils.load import load_variants
from loqusdb.constants import GRCH37, GRCH38


def test_load_variants(real_mongo_adapter, het_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with one heterozygote variant
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)
    mongo_variant = db.variant.find_one()

    assert mongo_variant == None

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH37)

    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant["families"] == [case_obj["case_id"]]
    assert mongo_variant["observations"] == 1
    assert mongo_variant["homozygote"] == 0
    assert mongo_variant["hemizygote"] == 0


def test_load_homozygote(real_mongo_adapter, hom_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with one homozygote variant
    db = mongo_adapter.db

    vcf = []
    vcf.append(hom_variant)
    assert db.variant.find_one() == None

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH37)
    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant["families"] == [case_obj["case_id"]]
    assert mongo_variant["observations"] == 1
    assert mongo_variant["homozygote"] == 1
    assert mongo_variant["hemizygote"] == 0


def test_load_hemizygote(real_mongo_adapter, hem_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with one hemizygote variant
    db = mongo_adapter.db

    vcf = []
    vcf.append(hem_variant)

    assert db.variant.find_one() == None

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH37)
    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant["families"] == [case_obj["case_id"]]
    assert mongo_variant["observations"] == 1
    assert mongo_variant["homozygote"] == 0
    assert mongo_variant["hemizygote"] == 1


def test_load_par_variant(real_mongo_adapter, par_variant, case_obj):
    mongo_adapter = real_mongo_adapter

    ## GIVEN an adapter and a vcf with one PAR variant
    db = mongo_adapter.db

    vcf = []
    vcf.append(par_variant)

    assert db.variant.find_one() == None

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH37)
    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant["families"] == [case_obj["case_id"]]
    assert mongo_variant["observations"] == 1
    assert mongo_variant["homozygote"] == 0
    assert mongo_variant["hemizygote"] == 0


def test_load_two_variants(real_mongo_adapter, het_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with tho heterygote variants
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)
    vcf.append(het_variant)

    ## WHEN loading the variants into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH37)

    ## THEN assert that the variant is loaded correct
    mongo_variant = db.variant.find_one()

    assert mongo_variant["observations"] == 2


def test_load_variants_skip_case_id(real_mongo_adapter, het_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with tho heterygote variants
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)

    ## WHEN loading the variants into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf,
        case_obj=case_obj,
        skip_case_id=True,
        genome_build=GRCH37,
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant.get("families") == None


def test_load_same_variant_different_case(real_mongo_adapter, het_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH37)

    case_id = case_obj["case_id"]
    case_id2 = "2"
    case_obj["case_id"] = case_id2

    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH37)

    mongo_variant = db.variant.find_one()

    assert mongo_variant["observations"] == 2
    assert mongo_variant["families"] == [case_id, case_id2]


def test_load_case_variants(real_mongo_adapter, case_obj):
    mongo_adapter = real_mongo_adapter

    db = mongo_adapter.db
    ## GIVEN a mongo adatper with snv variant file
    vcf_obj = VCF(case_obj["vcf_path"])
    ## WHEN loading the variants
    nr_variants = load_variants(
        adapter=mongo_adapter, vcf_obj=vcf_obj, case_obj=case_obj, genome_build=GRCH37
    )

    nr_loaded = 0
    for nr_loaded, variant in enumerate(db.variant.find(), 1):
        pass
    ## THEN assert that the correct number of variants was loaded
    assert nr_loaded > 0
    assert nr_loaded == case_obj["nr_variants"]


def test_load_sv_case_variants(mongo_adapter, sv_case_obj):
    db = mongo_adapter.db
    ## GIVEN a mongo adatper with snv variant file
    vcf_obj = VCF(sv_case_obj["vcf_sv_path"])
    ## WHEN loading the variants
    nr_variants = load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf_obj,
        case_obj=sv_case_obj,
        variant_type="sv",
        genome_build=GRCH37,
    )

    nr_loaded_svs = 0
    for nr_loaded_svs, variant in enumerate(db.structural_variant.find(), 1):
        pass
    nr_loaded_snvs = 0
    for nr_loaded_snvs, variant in enumerate(db.variant.find(), 1):
        pass
    ## THEN assert that the correct number of variants was loaded
    assert nr_loaded_svs > 0
    assert nr_loaded_snvs == 0
    assert nr_loaded_svs == sv_case_obj["nr_sv_variants"]


def test_load_variants_grch38(real_mongo_adapter, het_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with one heterozygote variant
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)
    mongo_variant = db.variant.find_one()

    assert mongo_variant == None

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH38)

    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant["families"] == [case_obj["case_id"]]
    assert mongo_variant["observations"] == 1
    assert mongo_variant["homozygote"] == 0
    assert mongo_variant["hemizygote"] == 0


def test_load_homozygote_grch38(real_mongo_adapter, hom_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with one homozygote variant
    db = mongo_adapter.db

    vcf = []
    vcf.append(hom_variant)
    assert db.variant.find_one() == None

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH38)
    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant["families"] == [case_obj["case_id"]]
    assert mongo_variant["observations"] == 1
    assert mongo_variant["homozygote"] == 1
    assert mongo_variant["hemizygote"] == 0


def test_load_hemizygote_grch38(real_mongo_adapter, variant_chr, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with one hemizygote variant
    db = mongo_adapter.db

    vcf = []
    vcf.append(variant_chr)

    assert db.variant.find_one() == None

    ## WHEN loading the variant into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf,
        case_obj=case_obj,
        genome_build=GRCH38,
        keep_chr_prefix=True,
    )
    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant["families"] == [case_obj["case_id"]]
    assert mongo_variant["observations"] == 1
    assert mongo_variant["homozygote"] == 0
    assert mongo_variant["hemizygote"] == 1


def test_load_par_variant_grch38(real_mongo_adapter, par_variant, case_obj):
    mongo_adapter = real_mongo_adapter

    ## GIVEN an adapter and a vcf with one PAR variant
    db = mongo_adapter.db

    vcf = []
    vcf.append(par_variant)

    assert db.variant.find_one() == None

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH38)
    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant["families"] == [case_obj["case_id"]]
    assert mongo_variant["observations"] == 1
    assert mongo_variant["homozygote"] == 0
    assert mongo_variant["hemizygote"] == 0


def test_load_two_variants_grch38(real_mongo_adapter, het_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with tho heterygote variants
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)
    vcf.append(het_variant)

    ## WHEN loading the variants into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH38)

    ## THEN assert that the variant is loaded correct
    mongo_variant = db.variant.find_one()

    assert mongo_variant["observations"] == 2


def test_load_variants_skip_case_id_grch38(real_mongo_adapter, het_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf with tho heterygote variants
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)

    ## WHEN loading the variants into the database
    load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf,
        case_obj=case_obj,
        skip_case_id=True,
        genome_build=GRCH37,
    )

    mongo_variant = db.variant.find_one()

    ## THEN assert that the variant is loaded correct
    assert mongo_variant.get("families") == None


def test_load_same_variant_different_case_grch38(real_mongo_adapter, het_variant, case_obj):
    mongo_adapter = real_mongo_adapter
    ## GIVEN an adapter and a vcf
    db = mongo_adapter.db

    vcf = []
    vcf.append(het_variant)

    ## WHEN loading the variant into the database
    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH38)

    case_id = case_obj["case_id"]
    case_id2 = "2"
    case_obj["case_id"] = case_id2

    load_variants(adapter=mongo_adapter, vcf_obj=vcf, case_obj=case_obj, genome_build=GRCH38)

    mongo_variant = db.variant.find_one()

    assert mongo_variant["observations"] == 2
    assert mongo_variant["families"] == [case_id, case_id2]


def test_load_case_variants_grch38(real_mongo_adapter, case_obj):
    mongo_adapter = real_mongo_adapter

    db = mongo_adapter.db
    ## GIVEN a mongo adatper with snv variant file
    vcf_obj = VCF(case_obj["vcf_path"])
    ## WHEN loading the variants
    nr_variants = load_variants(
        adapter=mongo_adapter, vcf_obj=vcf_obj, case_obj=case_obj, genome_build=GRCH38
    )

    nr_loaded = 0
    for nr_loaded, variant in enumerate(db.variant.find(), 1):
        pass
    ## THEN assert that the correct number of variants was loaded
    assert nr_loaded > 0
    assert nr_loaded == case_obj["nr_variants"]


def test_load_sv_case_variants_grch38(mongo_adapter, sv_case_obj):
    db = mongo_adapter.db
    ## GIVEN a mongo adatper with snv variant file
    vcf_obj = VCF(sv_case_obj["vcf_sv_path"])
    ## WHEN loading the variants
    nr_variants = load_variants(
        adapter=mongo_adapter,
        vcf_obj=vcf_obj,
        case_obj=sv_case_obj,
        variant_type="sv",
        genome_build=GRCH38,
    )

    nr_loaded_svs = 0
    for nr_loaded_svs, variant in enumerate(db.structural_variant.find(), 1):
        pass
    nr_loaded_snvs = 0
    for nr_loaded_snvs, variant in enumerate(db.variant.find(), 1):
        pass
    ## THEN assert that the correct number of variants was loaded
    assert nr_loaded_svs > 0
    assert nr_loaded_snvs == 0
    assert nr_loaded_svs == sv_case_obj["nr_sv_variants"]
