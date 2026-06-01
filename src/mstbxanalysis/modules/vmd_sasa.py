import click
import subprocess
import os

@click.command()
@click.option('--coord', required=True, help='Coordinate file [PDB, GRO, PSF, PARM7]')
@click.option('--traj', required=True, help='Trajectory file [DCD, XTC, NETCDF]')
@click.option('--sel1', default='protein', help='Selection for SASA calculation (VMD syntax)')
@click.option('--sel2', default='protein', help='Restricting selection (VMD syntax)')
@click.option('--srad', default=1.4, help='Solvent radius (default: 1.4 A)')
@click.option('--dt', default=0.002, help='Timestep in ns (default: 0.002)')
@click.option('--stride', default=1, help='Trajectory stride')
@click.option('--ofile', default='sasa.dat', help='Output file name')
def command(coord, traj, sel1, sel2, srad, dt, stride, ofile):
    """Calculate Surface Accessible Solvent Area (SASA) using VMD."""
    
    tcl_script = f"""
mol new {coord} waitfor all
mol addfile {traj} waitfor all

set outfile [open {ofile} w]
set nf [molinfo top get numframes]

for {{set i 0}} {{$i < $nf}} {{incr i {stride}}} {{
    set t [expr $i * {dt}]
    set sasa [measure sasa {srad} [atomselect top "{sel1}" frame $i] -restrict [atomselect top "{sel2}" frame $i]]
    puts $outfile "$t $sasa"
}}
close $outfile
exit
"""
    
    script_name = "tmp_sasa.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD SASA analysis...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"SASA analysis finished! Output written to: {ofile}")
