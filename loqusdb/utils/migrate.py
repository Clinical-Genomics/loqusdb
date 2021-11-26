import logging

from click import progressbar

LOG = logging.getLogger(__name__)


def migrate_database(adapter):
    """Migrate an old loqusdb instance to 1.0

    Args:
        adapter

    Returns:
        nr_updated(int): Number of variants that where updated
    """

    all_variants = adapter.get_variants()
    nr_variants = adapter.nr_variants()
    nr_updated = 0
    with progressbar(all_variants, label="Updating variants", length=nr_variants) as bar:
        for variant in bar:
            # Do not update if the variants have the correct format
            if "chrom" in variant:
                continue
            nr_updated += 1
            splitted_id = variant["_id"].split("_")

            chrom = splitted_id[0]
            start = int(splitted_id[1])
            ref = splitted_id[2]
            alt = splitted_id[3]

            # Calculate end
            end = start + (max(len(ref), len(alt)) - 1)

            adapter.db.variant.find_one_and_update(
                {"_id": variant["_id"]}, {"$set": {"chrom": chrom, "start": start, "end": end}}
            )

    return nr_updated
