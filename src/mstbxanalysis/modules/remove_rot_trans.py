import click
import os

@click.command()
@click.option('--top', required=True, help='Topology file [PSF/PDB].')
@click.option('--traj', required=True, help='Trajectory file [DCD/XTC].')
@click.option('--sel', default='protein', help='Selection based on VMD syntax to fit (e.g., "protein").')
@click.option('--ofile', default='prod_no_rot_trans.dcd', help='Output trajectory file name.')
def command(top, traj, sel, ofile):
    """Remove rotation and translation from a trajectory using VMD."""
    
    # Determine type for VMD mol addfile
    ext_traj = os.path.splitext(traj)[1][1:]
    if ext_traj.lower() == 'dcd':
        vmd_type = 'dcd'
    elif ext_traj.lower() == 'xtc':
        vmd_type = 'xtc'
    else:
        vmd_type = ext_traj

    tcl_script = f"""
package require pbctools 

# Load traj
mol new {top} waitfor all
mol addfile {traj} type {vmd_type} waitfor all

# selection 
set sel1 "{sel}"

# PBC wrap; often necessary before fitting if traj was unwrapped
pbc wrap -all -compound res -center bb -centersel "protein" 

# Remove rotation/translation by fitting to frame 0
set nf [ molinfo top get numframes ]
set ref [atomselect top "$sel1" frame 0]
set sel2 [atomselect top "$sel1"]
set all [atomselect top "all"]

for {{set i 0}} {{$i < $nf}} {{incr i}} {{
    $sel2 frame $i
    $all frame $i 
    $all move [measure fit $sel2 $ref]
}}

# Write file 
animate write {vmd_type} {ofile} beg 0 end -1 skip 1 waitfor all top 

quit
"""
    tcl_file = 'remove_rot_trans.tcl'
    with open(tcl_file, 'w') as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD to remove rot+trans from {traj}...")
    # Using 'vmd' instead of 'vmd4' as it's more standard, but user can override via PATH
    os.system(f"vmd -dispdev text -e {tcl_file}")
    
    if os.path.exists(ofile):
        click.echo(f"Rotation and translation removed. Output: {ofile}")
    else:
        click.echo("Error: Output trajectory was not created. Check VMD logs.")
