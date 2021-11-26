import pytest
from loqusdb.exceptions import CaseError
from loqusdb.utils.case import get_case


def test_get_family(case_lines):
    family = get_case(case_lines)
    assert family.family_id == "recessive_trio"


def test_get_multiple_families(two_cases):
    with pytest.raises(CaseError):
        family = get_case(two_cases)
