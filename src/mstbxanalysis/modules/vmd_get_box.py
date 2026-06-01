import click
import subprocess
import os

@click.command()
@click.option('--pdb', required=True, help='Input PDB file of the receptor')
@click.option('--sel', default='protein', help='Selection for box calculation (default: protein)')
@click.option('--ofile', default='box.dat', help='Output file name (default: box.dat)')
def command(pdb, sel, ofile):
    """Calculate center and box size for docking with AutoDock Vina or AutoDock4."""
    
    tcl_script = f"""
mol new {pdb}
set sel [atomselect top "{sel}"]
set geom [measure center $sel]
set minmax [measure minmax $sel]
set boxsize_vina [vecsub [lindex $minmax 1] [lindex $minmax 0]]
set ad4_x [expr [lindex $boxsize_vina 0]/0.375]
set ad4_y [expr [lindex $boxsize_vina 1]/0.375]
set ad4_z [expr [lindex $boxsize_vina 2]/0.375]
set boxsize_autodock [list $ad4_x $ad4_y $ad4_z]

set out_geom [open "{ofile}" w]
puts $out_geom "Center is: $geom"
puts $out_geom "Boxsize for VINA (1 spc): $boxsize_vina"
puts $out_geom "Boxsize for AUTODOCK (0.375 spc): $boxsize_autodock"
close $out_geom
exit
"""
    
    script_name = "tmp_get_box.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD to calculate box size...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"Box size calculation finished! Output written to: {ofile}")
