import pkg_resources


###### Files ######

# Background data

backround_svs = 'resources/loqusdb.20181005.gz'

###### Paths ######

# Backround data path

background_path = pkg_resources.resource_filename('loqusdb', backround_svs)
