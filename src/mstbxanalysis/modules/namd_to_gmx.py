import click
import parmed as pmd

@click.command()
@click.option('--psf', required=True, help='Input PSF file.')
@click.option('--pdb', required=True, help='Input PDB file.')
@click.option('--otop', default='structure_gmx.top', help='Output GMX TOP file.')
@click.option('--ogro', default='structure_gmx.gro', help='Output GMX GRO file.')
def command(psf, pdb, otop, ogro):
    """Convert NAMD PSF/PDB to GROMACS TOP/GRO format."""
    
    click.echo(f"Loading PSF: {psf}")
    struct_top = pmd.load_file(psf)
    struct_top.save(otop)
    click.echo(f"Saved GMX TOP to {otop}")

    click.echo(f"Loading PDB: {pdb}")
    struct_gro = pmd.load_file(pdb)
    struct_gro.save(ogro, format='gro')
    click.echo(f"Saved GMX GRO to {ogro}")
    
    click.echo("\nNote: If you encounter 'passed to fgets2 has size 4096' error in GROMACS,")
    click.echo("ensure all hidden files starting with '._' in the charmmff directory are removed.")
