import click
import MDAnalysis as mda
import pandas as pd
import warnings

# Suppress warnings from MDAnalysis
warnings.filterwarnings("ignore")

@click.command()
@click.option('--coord', required=True, help='Coordinate file [PDB/GRO, PSF, PARM7]')
@click.option('--traj', required=True, help='Trajectory file [XTC, DCD, NETCDF]')
@click.option('--sel', default='protein and name CA', help='Selection syntax based on MDAnalysis')
@click.option('--ofile', default='rmsd.dat', help='Output file name')
def command(coord, traj, sel, ofile):
    """Calculate Root Mean Square Deviation (RMSD) using MDAnalysis."""
    click.echo(f"Loading trajectory with coord={coord} and traj={traj}...")
    universe = mda.Universe(coord, traj)
    ref = universe

    from MDAnalysis.analysis import rms
    click.echo(f"Running RMSD analysis on selection: '{sel}'...")
    
    data = rms.RMSD(
        universe.select_atoms(sel),
        ref.select_atoms(sel),
        ref_frame=0
    )
    data.run()

    time = data.rmsd[:, 1] / 1000  # Convert to ns if originally in ps
    rmsd_values = data.rmsd[:, 2]

    df = pd.DataFrame({"time": time, "rmsd": rmsd_values})
    df.to_csv(ofile, index=False, sep="\t")
    
    click.echo(f"RMSD calculations finished! Output written to: {ofile}")
