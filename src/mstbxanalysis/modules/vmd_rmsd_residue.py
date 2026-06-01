import click
import subprocess
import os

@click.command()
@click.option('--pdb', required=True, help='Input PDB file')
@click.option('--traj', required=True, help='Input trajectory file')
@click.option('--sel', default='protein', help='Selection for calculation (default: protein)')
@click.option('--segid', default='PROA', help='Segid to calculate RMSD for (default: PROA)')
@click.option('--ofile', default='rmsd_residue.pdb', help='Output PDB file name (default: rmsd_residue.pdb)')
def command(pdb, traj, sel, segid, ofile):
    """Calculate RMSD per residue and map to beta column in VMD."""
    
    tcl_script = f"""
mol new {pdb} waitfor all
mol addfile {traj} waitfor all

set sel_resid [[atomselect top "{sel} and name CA"] get resid]

proc rmsd_residue_over_time {{mol res}} {{
    set reference [atomselect $mol "protein" frame 0]
    set compare [atomselect $mol "protein"]
    set all [atomselect top all]
    set num_steps [molinfo $mol get numframes]
    
    foreach r $res {{
	set rmsd($r) 0
    }}
    
    for {{set frame 0}} {{$frame < $num_steps}} {{incr frame}} {{
	puts "Calculating rmsd for frame $frame ..."
	$compare frame $frame
	set trans_mat [measure fit $compare $reference]
	$all move $trans_mat
	
	foreach r $res {{
	    set ref [atomselect $mol "segid {segid} and resid $r and noh" frame 0]
	    set comp [atomselect $mol "segid {segid} and resid $r and noh" frame $frame]
	    set rmsd($r) [expr $rmsd($r) + [measure rmsd $comp $ref]]
	    $comp delete
	    $ref delete
	}}
    }}
    set ave 0
	foreach r $res {{
	    set rmsd($r) [expr $rmsd($r)/$num_steps]
	    puts "RMSD of residue $r is $rmsd($r)"
	    set res_b [atomselect $mol "resid $r"] 
            $res_b set beta $rmsd($r)
            $res_b delete
	    set ave [expr $ave + $rmsd($r)]
	}}
    set ave [expr $ave/[llength $res]]
    puts " Average rmsd per residue:   $ave"
}}

rmsd_residue_over_time top $sel_resid
set all [atomselect top all]
$all writepdb {ofile}
exit
"""
    
    script_name = "tmp_rmsd_residue.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD RMSD per residue analysis...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"RMSD per residue analysis finished! Output written to: {ofile}")
