from loqusdb.utils.migrate import migrate_database


def test_migrate_one_variant(mongo_adapter):
    ##GIVEN a adapter to an empty old database
    adapter = mongo_adapter
    assert sum(1 for i in adapter.get_variants()) == 0

    ##WHEN inserting a old style variant and updating the database
    chrom = "1"
    pos = 880086
    ref = "T"
    alt = "C"
    hom = hem = 0
    obs = 3
    families = ["recessive_trio", "1", "2"]
    variant = {
        "_id": "_".join([chrom, str(pos), ref, alt]),
        "homozygote": hom,
        "hemizygote": hem,
        "observations": obs,
        "families": families,
    }
    adapter.db.variant.insert_one(variant)
    ##THEN assert that the variant was updated correct

    nr_updated = migrate_database(adapter)
    assert nr_updated == 1

    migrated_variant = adapter.db.variant.find_one()

    assert migrated_variant["chrom"] == chrom
    assert migrated_variant["start"] == pos
    assert migrated_variant["end"] == pos
    assert migrated_variant["homozygote"] == hom
    assert migrated_variant["hemizygote"] == hem
    assert migrated_variant["observations"] == obs
    assert migrated_variant["families"] == families
