import click
import MDAnalysis as mda
from MDAnalysis.analysis import diffusionmap, align
import matplotlib.pyplot as plt
import warnings

# Suppress warnings from MDAnalysis
warnings.filterwarnings("ignore")

@click.command()
@click.option('--coord', required=True, help='Coordinate file [GRO, PSF, PARM7, PDB]')
@click.option('--traj', required=True, help='Trajectory file [XTC, DCD, NETCDF, TRR]')
@click.option('--sel', default='protein and name CA', help='Selection syntax for 2D RMSD matrix')
@click.option('--ofile', default='2d_rmsd_matrix.svg', help='Output plot name (svg/png/pdf)')
def command(coord, traj, sel, ofile):
    """Calculate and plot a 2D RMSD Distance Matrix using MDAnalysis."""
    click.echo(f"Loading trajectory with coord={coord} and traj={traj}...")
    u = mda.Universe(coord, traj)
    
    click.echo(f"Aligning trajectory to itself using selection: '{sel}'...")
    align.AlignTraj(u, u, select=sel, in_memory=True).run()
    
    click.echo(f"Calculating Distance Matrix for selection: '{sel}'...")
    matrix = diffusionmap.DistanceMatrix(u, select=sel).run()
    
    # Plotting
    click.echo("Generating plot...")
    plt.rcParams['font.size'] = 12
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(matrix.results.dist_matrix, cmap="hsv", origin='lower')
    ax.set_xlabel("Molecular conformation [frame]")
    ax.set_ylabel("Molecular conformation [frame]")
    fig.colorbar(im, label=r'RMSD [$\AA$]')
    plt.tight_layout()
    plt.savefig(ofile, dpi=300, bbox_inches='tight')
    
    click.echo(f"2D RMSD Matrix finished! Plot saved to: {ofile}")
