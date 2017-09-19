import logging
from pkg_resources import get_distribution

from pymongo import (IndexModel, ASCENDING, DESCENDING)

logger = logging.getLogger(__name__)

__version__ = get_distribution("loqusdb").version

INDEXES = {
    'variant' : [IndexModel([
        ('chrom', ASCENDING),
        ('pos', ASCENDING),
        ('end', ASCENDING),
        ], name="coordinates"),
    ],
}