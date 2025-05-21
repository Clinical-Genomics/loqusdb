"""
tests/vcf_tools/check_par.py

Test if variants are in the Pseudo Autosomal Recessive region.
"""

from loqusdb.build_models.variant import check_par
from loqusdb.constants import GRCH37


def test_par_region_X_lower():
    chrom = "X"
    pos = 60001
    assert check_par(chrom, pos, GRCH37)


def test_par_region_X_middle():
    chrom = "X"
    pos = 1000000
    assert check_par(chrom, pos, GRCH37)


def test_par_region_X_upper():
    chrom = "X"
    pos = 2649520
    assert check_par(chrom, pos, GRCH37)


def test_par_region_X_second():
    chrom = "X"
    pos = 154931044
    assert check_par(chrom, pos, GRCH37)


def test_non_par_X_region():
    chrom = "X"
    pos = 60000
    assert not check_par(chrom, pos, GRCH37)


def test_par_wrong_chrom():
    chrom = "1"
    pos = 60000
    assert not check_par(chrom, pos, GRCH37)


def test_par_region_Y_lower():
    chrom = "Y"
    pos = 10001
    assert check_par(chrom, pos, GRCH37)


def test_par_region_Y_middle():
    chrom = "Y"
    pos = 1000000
    assert check_par(chrom, pos, GRCH37)


def test_par_region_Y_upper():
    chrom = "Y"
    pos = 2649520
    assert check_par(chrom, pos, GRCH37)


def test_par_region_Y_second():
    chrom = "Y"
    pos = 59034050
    assert check_par(chrom, pos, GRCH37)
