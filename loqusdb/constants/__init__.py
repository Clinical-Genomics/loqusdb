# Coordinates of pseudo autosomal region in Grch37

PAR = {
    'Y': [[10001, 2649520], [59034050, 59373566]],
    'X': [[60001, 2699520], [154931044, 155270560]]
}

# Map of cyvcf2 genotypes
GENOTYPE_MAP = {0: 'hom_ref', 1: 'het', 2: 'no_call', 3:'hom_alt'}

# To keep the order of chromosomes
CHROMOSOMES = ('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12',
               '13', '14', '15', '16', '17', '18', '19', '20', '21', '22', 'X',
               'Y', 'MT')

CHROM_TO_INT = {chrom:i+1 for i,chrom in enumerate(CHROMOSOMES)}