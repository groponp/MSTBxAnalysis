import click
import subprocess
import os

@click.command()
@click.argument('pdbs', nargs=-1, required=True)
@click.option('--ofile', default='merged.pdb', help='Output PDB file name (default: merged.pdb)')
@click.option('--opsf', default='merged.psf', help='Output PSF file name (default: merged.psf)')
def command(pdbs, ofile, opsf):
    """Merge multiple PDB files into one using VMD topotools."""
    
    pdb_list_str = " ".join(pdbs)
    tcl_script = f"""
package require topotools
set pdblist [list {pdb_list_str}]
set midlist [list ]
foreach pdb $pdblist {{
    set mid [mol new $pdb]
    lappend midlist $mid
}}
set mol [::TopoTools::mergemols $midlist]
animate write psf {opsf} $mol
animate write pdb {ofile} $mol
quit
"""
    
    script_name = "tmp_merge_pdb.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD to merge PDBs...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"Merging finished!")
    click.echo(f"Output PDB: {ofile}")
    click.echo(f"Output PSF: {opsf}")
