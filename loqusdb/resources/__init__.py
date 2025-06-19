from importlib.resources import files, as_file

from loqusdb.constants import GRCH37, GRCH38

###### Files ######

# Background data
PATH_NAME = "loqusdb.resources"

backround_svs = "loqusdb.20181005.gz"
maf_50_grch37 = "maf_50_sites_GRCh37.vcf.gz"
maf_50_grch38 = "maf_50_sites_GRCh38.vcf.gz"

### Profile SNPs for Grch37 and 38

###### Paths ######

# Backround data path

background_path = str(files(PATH_NAME).joinpath(backround_svs))

maf_grch37_path = str(files(PATH_NAME).joinpath(maf_50_grch37))
maf_grch38_path = str(files(PATH_NAME).joinpath(maf_50_grch38))

MAF_PATH = {GRCH37: maf_grch37_path, GRCH38: maf_grch38_path}
