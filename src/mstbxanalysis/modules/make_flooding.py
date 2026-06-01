import click
import os
import numpy as np
import MDAnalysis as mda
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')

@click.command()
@click.option('--conc', required=True, type=float, help='Concentration in mol/L.')
@click.option('--boxvol', required=True, type=float, help='Box volume in A^3.')
@click.option('--pdbi', required=True, help='Protein PDB file.')
@click.option('--lig', required=True, help='Ligand PDB file.')
@click.option('--maxz', required=True, type=float, help='Maximum Z distance for solute.')
@click.option('--lipid-pdb', default='step4_lipid.pdb', help='Lipid PDB file.')
def command(conc, boxvol, pdbi, lig, maxz, lipid_pdb):
    """Create PDB input for concentration-based Flooding MD using packmol."""
    
    click.echo("Calculating flooding parameters...")
    
    # Constants from legacy script
    navo = 6.022e23
    wvol = 31.05 # volume per water molecule in A^3
    
    # n_wat = boxvol / wvol
    # n_ions = 0.0187 * conc * n_wat
    number_water = boxvol / wvol
    number_mol = int(np.round(0.0187 * conc * number_water))
    
    click.echo(f"Box Volume: {boxvol} A^3")
    click.echo(f"Concentration: {conc} mol/L")
    click.echo(f"Calculated Ligands to add: {number_mol}")

    # Load with MDAnalysis to get dimensions
    u = mda.Universe(pdbi)
    protein = u.select_atoms("protein")
    if len(protein) == 0:
        click.echo("Warning: No protein found, using all atoms for box dimensions.")
        sel_for_box = u.atoms
    else:
        sel_for_box = protein

    # Min/Max coordinates
    # protein.bbox() returns [xmin, ymin, zmin, xmax, ymax, zmax]
    bbox = sel_for_box.bbox()
    xmin, ymin, zmin = bbox[0] - 10, bbox[1] - 10, bbox[2]
    xmax, ymax, zmax = bbox[3] + 10, bbox[4] + 10, bbox[5]
    
    lzp = zmax + 5
    
    click.echo(f"Placement box: x=[{xmin}, {xmax}], y=[{ymin}, {ymax}], z=[{lzp}, {maxz}]")

    # Generate packmol input
    packmol_input = f"""
tolerance 2.0
filetype pdb
output pack_{conc}.pdb
seed -1
avoid_overlap yes
nloop 1000

structure {lipid_pdb}
    centerofmass
    fixed 0. 0. 0. 0. 0. 0.
end structure

structure {lig}
    number {number_mol}
    resnumbers 3
    inside box {xmin:.2f} {ymin:.2f} {lzp:.2f} {xmax:.2f} {ymax:.2f} {maxz:.2f}
end structure
"""
    with open("pack.inp", "w") as f:
        f.write(packmol_input)
    
    click.echo("Running packmol...")
    os.system("packmol < pack.inp")
    
    if os.path.exists(f"pack_{conc}.pdb"):
        click.echo(f"Flooding system created: pack_{conc}.pdb")
    else:
        click.echo("Error: packmol failed to create output.")
