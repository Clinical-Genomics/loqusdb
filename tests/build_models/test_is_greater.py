from loqusdb.build_models.variant import Position, is_greater
from loqusdb.constants import GRCH37, GRCH38


def test_is_greater_different_chrom():
    ## GIVEN two positions where a is smaller than b. Different chroms
    a = Position("1", 100)
    b = Position("3", 100)

    ## WHEN testing if a is greater than b
    res = is_greater(a, b, genome_build=GRCH37)
    ## THEN assert a was not greater than b
    assert res is False

    ## WHEN testing if b is greater than a
    res = is_greater(b, a, genome_build=GRCH37)
    ## THEN assert b was greater than a
    assert res is True


def test_is_greater_same_chrom():
    ## GIVEN two positions where a is smaller than b. Same chroms
    a = Position("1", 100)
    b = Position("1", 300)

    ## WHEN testing if a is greater than b
    res = is_greater(a, b, genome_build=GRCH37)
    ## THEN assert a was not greater than b
    assert res is False

    ## WHEN testing if b is greater than a
    res = is_greater(b, a, genome_build=GRCH37)
    ## THEN assert b was greater than a
    assert res is True


def test_is_greater_wierd_chrom():
    ## GIVEN two positions where one chrom is unknown b
    a = Position("1", 100)
    b = Position("GRLrs2", 300)

    ## WHEN testing if a is greater than b
    res = is_greater(a, b, genome_build=GRCH37)
    ## THEN assert a was not greater than b
    assert res is False

    ## WHEN testing if b is greater than a
    res = is_greater(b, a, genome_build=GRCH37)
    ## THEN assert a was not greater than b
    assert res is False


def test_is_greater_different_chrom_grch38():
    ## GIVEN two positions where a is smaller than b. Different chroms
    a = Position("chr1", 100)
    b = Position("chr3", 100)

    ## WHEN testing if a is greater than b
    res = is_greater(a, b, genome_build=GRCH38)
    ## THEN assert a was not greater than b
    assert res is False

    ## WHEN testing if b is greater than a
    res = is_greater(b, a, genome_build=GRCH38)
    ## THEN assert b was greater than a
    assert res is True


def test_is_greater_same_chrom_grch38():
    ## GIVEN two positions where a is smaller than b. Same chroms
    a = Position("chr1", 100)
    b = Position("chr1", 300)

    ## WHEN testing if a is greater than b
    res = is_greater(a, b, genome_build=GRCH38)
    ## THEN assert a was not greater than b
    assert res is False

    ## WHEN testing if b is greater than a
    res = is_greater(b, a, genome_build=GRCH38)
    ## THEN assert b was greater than a
    assert res is True


def test_is_greater_wierd_chrom_grch38():
    ## GIVEN two positions where one chrom is unknown b
    a = Position("chr1", 100)
    b = Position("GRLrs2", 300)

    ## WHEN testing if a is greater than b
    res = is_greater(a, b, genome_build=GRCH38)
    ## THEN assert a was not greater than b
    assert res is False

    ## WHEN testing if b is greater than a
    res = is_greater(b, a, genome_build=GRCH38)
    ## THEN assert a was not greater than b
    assert res is False
