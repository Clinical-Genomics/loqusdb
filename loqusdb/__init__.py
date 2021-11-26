import logging

from pkg_resources import get_distribution
from pymongo import ASCENDING, IndexModel

logger = logging.getLogger(__name__)

__version__ = get_distribution("loqusdb").version

INDEXES = {
    "variant": [
        IndexModel(
            [
                ("chrom", ASCENDING),
                ("start", ASCENDING),
                ("end", ASCENDING),
            ],
            name="coordinates",
        ),
        IndexModel(
            [
                ("chrom", ASCENDING),
                ("end", ASCENDING),
            ],
            name="end",
        ),
    ],
    "structural_variant": [
        IndexModel(
            [
                ("chrom", ASCENDING),
                ("end_chrom", ASCENDING),
                ("sv_type", ASCENDING),
                ("pos_left", ASCENDING),
            ],
            name="coordinates",
        ),
        IndexModel(
            [
                ("chrom", ASCENDING),
                ("pos_left", ASCENDING),
                ("end_right", ASCENDING),
            ],
            name="short_coordinates",
        ),
    ],
    "identity": [
        IndexModel(
            [
                ("cluster_id", ASCENDING),
            ],
            name="cluster",
        ),
        IndexModel(
            [
                ("variant_id", ASCENDING),
            ],
            name="variant",
        ),
    ],
}

CHROMOSOME_ORDER = (
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "13",
    "14",
    "15",
    "16",
    "17",
    "18",
    "19",
    "20",
    "21",
    "22",
    "23",
    "X",
    "Y",
    "MT",
)
