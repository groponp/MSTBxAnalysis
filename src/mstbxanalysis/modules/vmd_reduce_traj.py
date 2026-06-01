import click
import subprocess
import os

@click.command()
@click.option('--psf', required=True, help='Input PSF file')
@click.option('--dcd', required=True, help='Input DCD trajectory file')
@click.option('--stride', default=100, help='Trajectory stride (skip) (default: 100)')
@click.option('--ofile', default='reduce.dcd', help='Output DCD file name (default: reduce.dcd)')
def command(psf, dcd, stride, ofile):
    """Reduce trajectory size by applying a stride in VMD."""
    
    tcl_script = f"""
mol new {psf} type psf waitfor all
mol addfile {dcd} type dcd first 0 last -1 

animate write dcd {ofile} beg 0 end -1 skip {stride} waitfor all top
quit  
"""
    
    script_name = "tmp_reduce_traj.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD to reduce trajectory...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"Trajectory reduction finished! Output written to: {ofile}")
