import click
import MDAnalysis as mda
import warnings

# Suppress warnings from MDAnalysis
warnings.filterwarnings("ignore")

@click.command()
@click.option('--icoord', required=True, help='Input coordinate file [GRO, PSF, PARM7, PDB]')
@click.option('--itraj', required=True, help='Input trajectory file [XTC, DCD, NETCDF, TRR]')
@click.option('--ocoord', required=True, help='Output coordinate file name')
@click.option('--otraj', required=True, help='Output trajectory file name')
@click.option('--sel', default='all', help='Selection syntax to filter atoms')
def command(icoord, itraj, ocoord, otraj, sel):
    """Convert coordinates and trajectories between different formats using MDAnalysis."""
    click.echo(f"Loading input: {icoord} and {itraj}...")
    u = mda.Universe(icoord, itraj)
    
    click.echo(f"Selecting atoms: '{sel}'...")
    selected_atoms = u.select_atoms(sel)
    
    click.echo(f"Writing output coordinate: {ocoord}...")
    selected_atoms.write(ocoord)
    
    click.echo(f"Writing output trajectory: {otraj}...")
    with mda.Writer(otraj, selected_atoms.n_atoms) as W:
        for ts in u.trajectory:
            W.write(selected_atoms)
    
    click.echo("Conversion finished successfully!")
