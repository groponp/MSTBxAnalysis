import click
import subprocess
import os

@click.command()
@click.option('--pdb', required=True, help='Input PDB file')
@click.option('--rbd_sel', default='protein and resid 509 to 541', help='Selection for RBD (default: resid 509-541)')
@click.option('--rbm_sel', default='protein and resid 437 to 508', help='Selection for RBM (default: resid 437-508)')
@click.option('--ntd_sel', default='protein and resid 13 to 303', help='Selection for NTD (default: resid 13-303)')
@click.option('--s1_sel', default='protein and resid 304 to 685', help='Selection for S1 (default: resid 304-685)')
@click.option('--s2_sel', default='protein and resid 686 to 1273', help='Selection for S2 (default: resid 686-1273)')
@click.option('--ofile', default='renamed.pdb', help='Output PDB file name (default: renamed.pdb)')
def command(pdb, rbd_sel, rbm_sel, ntd_sel, s1_sel, s2_sel, ofile):
    """Assign segment names based on residue ranges (default for Spike protein)."""
    
    tcl_script = f"""
mol new {pdb} type pdb waitfor all

set rbd [atomselect top "{rbd_sel}"]
set rbm [atomselect top "{rbm_sel}"]
set ntd [atomselect top "{ntd_sel}"]
set s1 [atomselect top "{s1_sel}"]
set s2 [atomselect top "{s2_sel}"]

if {{ [$rbd num] > 0 }} {{ $rbd set segid "RBD" }}
if {{ [$rbm num] > 0 }} {{ $rbm set segid "RBM" }}
if {{ [$ntd num] > 0 }} {{ $ntd set segid "NTD" }}
if {{ [$s1 num] > 0 }} {{ $s1  set segid "S1" }}
if {{ [$s2 num] > 0 }} {{ $s2  set segid "S2" }}

set all [atomselect top "all"]
$all writepdb {ofile}
quit
"""
    
    script_name = "tmp_make_segname.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD to assign segnames...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"Segname assignment finished! Output written to: {ofile}")
