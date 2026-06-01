import click
import MDAnalysis as mda
import numpy as np
from MDAnalysis.analysis import distances
import pandas as pd
import warnings

# Suppress warnings from MDAnalysis
warnings.filterwarnings('ignore')

@click.command()
@click.option('--top', required=True, help='Topology file.')
@click.option('--traj', multiple=True, required=True, help='Trajectory file(s). Can be specified multiple times.')
@click.option('--sel1', required=True, help='Selection 1 (e.g., RBD).')
@click.option('--sel2', required=True, help='Selection 2 (e.g., Antibody Chain B).')
@click.option('--sel3', help='Selection 3 (optional, e.g., Antibody Chain C).')
@click.option('--cutoff', default=7.0, type=float, help='Cut-off distance for contacts (Angstrom).')
@click.option('--ratio', default=0.7, type=float, help='Ratio threshold for filtering contacts.')
@click.option('--ofile', default='contacts.csv', help='Output base name.')
@click.option('--frames', default=-1, type=int, help='Number of frames to analyze (-1 for all).')
def command(top, traj, sel1, sel2, sel3, cutoff, ratio, ofile, frames):
    """Calculate contact frequency between selections along a trajectory."""
    
    click.echo(f"Loading topology: {top}")
    click.echo(f"Loading trajectories: {traj}")
    u = mda.Universe(top, list(traj))
    nframes = len(u.trajectory)
    
    if frames != -1:
        nframes = min(frames, nframes)
    
    group1 = u.select_atoms(sel1)
    group2 = u.select_atoms(sel2)
    
    n_g1 = len(group1)
    n_g2 = len(group2)
    
    if n_g1 == 0 or n_g2 == 0:
        click.echo("Error: One of the selections returned no atoms.")
        return

    contact_sum_12 = np.zeros((n_g1, n_g2))
    
    if sel3:
        group3 = u.select_atoms(sel3)
        n_g3 = len(group3)
        if n_g3 > 0:
            contact_sum_13 = np.zeros((n_g1, n_g3))
        else:
            sel3 = None
            click.echo("Warning: Selection 3 returned no atoms. Skipping.")

    click.echo(f"Analyzing {nframes} frames...")
    
    for i, ts in enumerate(u.trajectory[:nframes]):
        p1 = group1.positions
        p2 = group2.positions
        
        dist12 = distances.distance_array(p1, p2, box=u.dimensions)
        dist12[dist12 < cutoff] = 1
        dist12[dist12 >= cutoff] = 0
        contact_sum_12 += dist12
        
        if sel3:
            p3 = group3.positions
            dist13 = distances.distance_array(p1, p3, box=u.dimensions)
            dist13[dist13 < cutoff] = 1
            dist13[dist13 >= cutoff] = 0
            contact_sum_13 += dist13
        
        if (i + 1) % 50 == 0 or (i + 1) == nframes:
            click.echo(f"Processed frame {i+1}/{nframes}")

    contact_ratio_12 = contact_sum_12 / nframes
    df12 = pd.DataFrame(contact_ratio_12)
    df12_filtered = df12.where(df12 > ratio)
    
    out12 = f"sel1_sel2_{ofile}"
    df12_filtered.to_csv(out12)
    click.echo(f"Results for sel1-sel2 written to {out12}")
    
    if sel3:
        contact_ratio_13 = contact_sum_13 / nframes
        df13 = pd.DataFrame(contact_ratio_13)
        df13_filtered = df13.where(df13 > ratio)
        out13 = f"sel1_sel3_{ofile}"
        df13_filtered.to_csv(out13)
        click.echo(f"Results for sel1-sel3 written to {out13}")

    click.echo("Contact map analysis complete.")
