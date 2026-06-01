import click
import subprocess
import os

@click.command()
@click.option('--pdb', required=True, help='Input PDB file')
@click.option('--lig_sel', default='resname TYL and noh', help='Selection for ligand pulling (default: resname TYL and noh)')
@click.option('--helix_sel', default='protein and helix', help='Selection for fixing helix (default: protein and helix)')
@click.option('--mark1', default=1.0, help='Mark for ligand (default: 1.0)')
@click.option('--mark2', default=2.0, help='Mark for helix (default: 2.0)')
@click.option('--ofile', default='marks_lig_helixs_ca.pdb', help='Output PDB file name')
def command(pdb, lig_sel, helix_sel, mark1, mark2, ofile):
    """Mark atoms into B-column of a PDB file for NAMD TclForces processing."""
    
    tcl_script = f"""
mol new {pdb} type pdb waitfor all 

set ligmark "{lig_sel}"
set helixmark "{helix_sel}"

set mark1 "{mark1}"
set mark2 "{mark2}"

set all [atomselect top all] 
$all set beta 0 
$all set occupancy 0 

set lig [atomselect top $ligmark] 
if {{ [$lig num] > 0 }} {{
    set ligmass [$lig get mass] 
    $lig set beta $mark1
    $lig set occupancy $ligmass 
}}

set helix [atomselect top $helixmark] 
if {{ [$helix num] > 0 }} {{
    set helixmass [$helix get mass] 
    $helix set beta $mark2 
    $helix set occupancy $helixmass 
}}

$all writepdb {ofile} 
quit 
"""
    
    script_name = "tmp_make_tclforces.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD to mark PDB for TclForces...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"PDB marking finished! Output written to: {ofile}")
