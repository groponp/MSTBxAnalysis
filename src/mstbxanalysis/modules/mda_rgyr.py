import click
import MDAnalysis as mda
import pandas as pd
import warnings

# Suppress warnings from MDAnalysis
warnings.filterwarnings("ignore")

@click.command()
@click.option('--coord', required=True, help='Coordinate file [GRO, PSF, PARM7, PDB]')
@click.option('--traj', required=True, help='Trajectory file [XTC, DCD, NETCDF, TRR]')
@click.option('--sel', default='protein and name CA', help='Selection syntax based on MDAnalysis')
@click.option('--ofile', default='rgyr.dat', help='Output file name')
def command(coord, traj, sel, ofile):
    """Calculate Radius of Gyration (Rgyr) using MDAnalysis."""
    click.echo(f"Loading trajectory with coord={coord} and traj={traj}...")
    u = mda.Universe(coord, traj)
    selection = u.select_atoms(sel)
    
    rgyr_values = []
    time_values = []
    
    click.echo(f"Running Rgyr analysis on selection: '{sel}'...")
    for ts in u.trajectory:
        time_values.append(u.trajectory.time / 1000)  # Convert to ns
        rgyr_values.append(selection.radius_of_gyration())
    
    df = pd.DataFrame({"time": time_values, "rgyr": rgyr_values})
    df.to_csv(ofile, index=False, sep="\t")
    
    click.echo(f"Rgyr calculations finished! Output written to: {ofile}")
