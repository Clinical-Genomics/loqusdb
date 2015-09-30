import click

@click.group()
@click.argument('variant_file',
                    nargs=1,
                    type=click.File('r'),
                    metavar='<vcf_file> or -'
)
@click.option('-f', '--family_file',
                    nargs=1, 
                    type=click.File('r'),
                    metavar='<ped_file>'
)
@click.option('-t' ,'--family_type', 
                type=click.Choice(['ped', 'alt', 'cmms', 'mip']), 
                default='ped',
                help='If the analysis use one of the known setups, please specify which one.'
)
def cli(variant_file, family_file, family_type):
    """Tool for manipulating a variant frequency database
    
    """
    pass


if __name__ == '__main__':
    cli()
