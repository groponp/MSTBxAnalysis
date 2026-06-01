import click
import MDAnalysis as mda
import numpy as np
import pandas as pd
import warnings

# Suppress warnings from MDAnalysis
warnings.filterwarnings('ignore')

@click.command()
@click.option('--top', required=True, help='Topology file.')
@click.option('--traj', required=True, help='Trajectory file.')
@click.option('--sel', multiple=True, required=True, help='Atom selection(s) to analyze. Can be specified multiple times.')
@click.option('--temp', default=298.0, type=float, help='Temperature in Kelvin.')
@click.option('--axis', default='z', type=click.Choice(['x', 'y', 'z', 'all']), help='Axis to analyze.')
def command(top, traj, sel, temp, axis):
    """Calculate spring constant K for umbrella sampling based on coordinate fluctuations."""
    
    u = mda.Universe(top, traj)
    groups = [u.select_atoms(s) for s in sel]
    
    if any(len(g) == 0 for g in groups):
        click.echo("Error: One or more selections returned no atoms.")
        return

    n_frames = len(u.trajectory)
    n_groups = len(groups)
    
    # Store positions
    # If axis is 'all', we might want the magnitude? 
    # Or just individual x, y, z? 
    # Usually US is along one dimension.
    
    pos_data = np.zeros((n_frames, n_groups))
    
    axis_idx = {'x': 0, 'y': 1, 'z': 2}

    click.echo(f"Processing {n_frames} frames for {n_groups} groups...")
    for i, ts in enumerate(u.trajectory):
        for j, g in enumerate(groups):
            com = g.center_of_mass()
            if axis == 'all':
                # If all, maybe the user wants the distance from a reference?
                # For now, let's use the norm of the COM vector.
                pos_data[i, j] = np.linalg.norm(com)
            else:
                pos_data[i, j] = com[axis_idx[axis]]
        
        if (i + 1) % 100 == 0 or (i + 1) == n_frames:
            click.echo(f"Frame {i+1}/{n_frames}")

    # Calculate variance and K
    # kus = (kb * T) / variance
    # Note: Na is often included if we want kJ/mol*A^2
    kb = 1.380649e-23   # J/K
    Na = 6.02214076e23  # mol^-1
    
    # Standard deviation in Angstrom
    stds = np.std(pos_data, axis=0)
    variances_sq_ang = np.var(pos_data, axis=0) # in A^2
    
    # K = (kb * T * Na) / variance
    # kb * Na = R (gas constant)
    R = kb * Na # J/(mol*K)
    
    # We need to be careful with units. 
    # If variance is in A^2, then K is in J/(mol * A^2)
    # Convert J to kJ: / 1000
    
    kus_kJ = (R * temp) / variances_sq_ang / 1000.0
    kus_kcal = kus_kJ * 0.239006
    
    click.echo("\nResults:")
    click.echo("==========================")
    for j, s in enumerate(sel):
        click.echo(f"Selection: {s}")
        click.echo(f"  Std Dev ({axis}): {stds[j]:.4f} A")
        click.echo(f"  K: {kus_kJ[j]:.4f} kJ/mol*A^2")
        click.echo(f"  K: {kus_kcal[j]:.4f} kcal/mol*A^2")
    
    click.echo("\nDone.")
