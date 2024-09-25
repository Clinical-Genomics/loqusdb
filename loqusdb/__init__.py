import logging

from pymongo import ASCENDING, IndexModel

logger = logging.getLogger(__name__)

__version__ = "2.7.9"

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
                ("sv_type", ASCENDING),
                ("chrom", ASCENDING),
                ("end_chrom", ASCENDING),
                ("pos_left", ASCENDING),
                ("pos_right", ASCENDING),
            ],
            name="coordinates",
            background=True,
        ),
        IndexModel(
            [
                ("chrom", ASCENDING),
                ("pos_left", ASCENDING),
                ("end_right", ASCENDING),
            ],
            name="short_coordinates",
            background=True,
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
