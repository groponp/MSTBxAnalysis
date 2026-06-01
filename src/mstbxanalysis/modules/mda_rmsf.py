import click
import MDAnalysis as mda
from MDAnalysis.analysis import rms, align
import pandas as pd
import warnings

# Suppress warnings from MDAnalysis
warnings.filterwarnings("ignore")

@click.command()
@click.option('--coord', required=True, help='Coordinate file [GRO, PSF, PARM7, PDB]')
@click.option('--traj', required=True, help='Trajectory file [XTC, DCD, NETCDF, TRR]')
@click.option('--sel', default='protein and name CA', help='Selection syntax for alignment and RMSF')
@click.option('--ofile', default='rmsf.dat', help='Output data file name')
@click.option('--opdb', default='rmsf_to_beta.pdb', help='Output PDB with RMSF in B-factor column')
def command(coord, traj, sel, ofile, opdb):
    """Calculate Root Mean Square Fluctuation (RMSF) using MDAnalysis."""
    click.echo(f"Loading trajectory with coord={coord} and traj={traj}...")
    u = mda.Universe(coord, traj)
    
    click.echo(f"Aligning trajectory to average structure using selection: '{sel}'...")
    average = align.AverageStructure(u, u, select=sel, ref_frame=0).run()
    ref = average.results.universe
    align.AlignTraj(u, ref, select=sel).run()
    
    click.echo(f"Calculating RMSF for selection: '{sel}'...")
    target_atoms = u.select_atoms(sel)
    rmsf_analysis = rms.RMSF(target_atoms).run()
    
    df = pd.DataFrame({"resid": target_atoms.resids, "rmsf": rmsf_analysis.results.rmsf})
    df.to_csv(ofile, index=False, sep="\t")
    click.echo(f"RMSF data written to: {ofile}")
    
    # Save to PDB B-factor
    u.add_TopologyAttr('tempfactors')
    # Map RMSF values to atoms
    for residue, r_value in zip(target_atoms.residues, rmsf_analysis.results.rmsf):
        residue.atoms.tempfactors = r_value
    
    target_atoms.write(opdb)
    click.echo(f"PDB with RMSF values saved to: {opdb}")
    
    click.echo("RMSF calculation finished!")
