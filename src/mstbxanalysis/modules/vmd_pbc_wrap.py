import click
import subprocess
import os

@click.command()
@click.option('--psf', required=True, help='Input PSF file')
@click.option('--dcd', required=True, help='Input DCD trajectory file')
@click.option('--sel_wrap', default='protein', help='Selection for wrapping (default: protein)')
@click.option('--sel_traj', default='all', help='Selection for writing wrapped trajectory (default: all)')
@click.option('--sel_fit', default='protein and name CA', help='Selection for alignment/fitting (default: protein and name CA)')
@click.option('--is_mem', is_flag=True, help='Flag if system is a membrane system')
@click.option('--ofile_pbc', default='traj_noPBC.dcd', help='Output name for wrapped trajectory')
@click.option('--ofile_fit', default='traj_noPBC_fitAtomsGroup.dcd', help='Output name for wrapped and fitted trajectory')
def command(psf, dcd, sel_wrap, sel_traj, sel_fit, is_mem, ofile_pbc, ofile_fit):
    """Remove PBC and rot+trans effects using VMD pbctools."""
    
    mem_val = 1 if is_mem else 0
    prot_val = 0 if is_mem else 1
    
    tcl_script = f"""
package require pbctools 

mol new {psf} type psf 
mol addfile {dcd} type dcd waitfor all 

set mem {mem_val} 
set prot {prot_val} 
set seltxtwrap "{sel_wrap}"
set seltxttraj  "{sel_traj}"

proc fitAtomGroup {{mol sel }} {{ 
	set ref [atomselect $mol $sel frame 0]
	set fitAtoms [atomselect $mol $sel]
	set nf [molinfo $mol get numframes]
	set moveAtoms [atomselect $mol all] 
	for {{set frame 0}} {{ $frame < $nf }} {{ incr frame }} {{
		puts "Frame: $frame"
		$fitAtoms frame $frame
		$moveAtoms frame $frame 
		set matrix [measure fit $fitAtoms $ref]
		$moveAtoms move $matrix   		
	}}
	animate write dcd {ofile_fit} beg 0 end -1 waitfor all top
}}

if {{ $mem == 1}} {{
	pbc wrap -center com -centersel $seltxtwrap -all -compound res
	set sel [atomselect top $seltxttraj]
	animate write dcd {ofile_pbc} beg 0 end -1 waitfor all sel $sel
       	
}} elseif {{ $prot == 1 }} {{
	pbc wrap -center com -centersel $seltxtwrap -all -compound res 
	set sel [atomselect top $seltxttraj]
	animate write dcd {ofile_pbc} beg 0 end -1 waitfor all sel $sel 
}}

mol delete all 
mol new {psf} type psf 
mol addfile {ofile_pbc} type dcd waitfor all 

set seltxt "{sel_fit}"
fitAtomGroup top  $seltxt 

quit 
"""
    
    script_name = "tmp_pbc_wrap.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD PBC wrap and fit...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"PBC wrapping and fitting finished!")
    click.echo(f"Wrapped trajectory: {ofile_pbc}")
    click.echo(f"Fitted trajectory: {ofile_fit}")
