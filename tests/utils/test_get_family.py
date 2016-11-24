import pytest

from loqusdb.utils import get_family
from loqusdb.exceptions import CaseError

def test_get_family(case_lines):
    family = get_family(case_lines)
    assert family.family_id == 'recessive_trio'

def test_get_multiple_families(two_cases):
    with pytest.raises(CaseError):
        family = get_family(two_cases)