import logging

from pymongo import ASCENDING, IndexModel

logger = logging.getLogger(__name__)

__version__ = "2.7.21"

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
