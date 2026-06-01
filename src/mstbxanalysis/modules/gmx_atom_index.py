import click
import MDAnalysis as mda
import os
import warnings

# Suppress warnings from MDAnalysis
warnings.filterwarnings("ignore")

@click.command()
@click.option('--coord', required=True, help='Coordinate file [GRO, PDB]')
@click.option('--sel', required=True, help='Selection syntax based on MDAnalysis')
@click.option('--name', required=True, help='Name for the new index group')
@click.option('--ndx-file', default='index_array.ndx', help='Output index file name')
@click.option('--init', is_flag=True, help='If set, initialize a dummy index using GROMACS make_ndx first')
def command(coord, sel, name, ndx_file, init):
    """Create or append to a GROMACS index file (.ndx) using MDAnalysis selections."""
    
    if init:
        click.echo("Initializing dummy index using GROMACS make_ndx...")
        # Note: This assumes GROMACS is installed and 'em.gro' exists as per original script logic
        # but we can try to be more generic if needed.
        os.system(f"echo \"q\\n\" | gmx make_ndx -f {coord} -o {ndx_file}")

    click.echo(f"Loading coordinate: {coord}...")
    u = mda.Universe(coord)
    
    click.echo(f"Selecting atoms: '{sel}'...")
    selected_atoms = u.select_atoms(sel)
    
    click.echo(f"Writing group '{name}' to {ndx_file}...")
    with mda.selections.gromacs.SelectionWriter(ndx_file, mode='a') as ndx:
        ndx.write(selected_atoms, name=name)
    
    click.echo("Index creation finished!")
