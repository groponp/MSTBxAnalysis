import click
import parmed as pmd

@click.command()
@click.option('--psf', required=True, help='Input PSF file.')
@click.option('--pdb', required=True, help='Input PDB file.')
@click.option('--opsf', default='structure_charmm.psf', help='Output CHARMM PSF file.')
@click.option('--ocrd', default='structure_charmm.crd', help='Output CHARMM CRD file.')
def command(psf, pdb, opsf, ocrd):
    """Convert NAMD PSF/PDB to CHARMM PSF/CRD format."""
    
    click.echo(f"Loading PSF: {psf}")
    struct_psf = pmd.load_file(psf)
    struct_psf.save(opsf)
    click.echo(f"Saved CHARMM PSF to {opsf}")

    click.echo(f"Loading PDB: {pdb}")
    struct_pdb = pmd.load_file(pdb)
    struct_pdb.save(ocrd, format='charmmcrd')
    click.echo(f"Saved CHARMM CRD to {ocrd}")
