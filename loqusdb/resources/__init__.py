import pkg_resources

from loqusdb.constants import GRCH37, GRCH38

###### Files ######

# Background data

backround_svs = "resources/loqusdb.20181005.gz"
maf_50_grch37 = "resources/maf_50_sites_GRCh37.vcf.gz"
maf_50_grch38 = "resources/maf_50_sites_GRCh38.vcf.gz"

### Profile SNPs for Grch37 and 38

###### Paths ######

# Backround data path

background_path = pkg_resources.resource_filename("loqusdb", backround_svs)

maf_grch37_path = pkg_resources.resource_filename("loqusdb", maf_50_grch37)
maf_grch38_path = pkg_resources.resource_filename("loqusdb", maf_50_grch38)

MAF_PATH = {GRCH37: maf_grch37_path, GRCH38: maf_grch38_path}
