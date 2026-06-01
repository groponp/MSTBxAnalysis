import click
import subprocess
import os

@click.command()
@click.option('--pdb', required=True, help='Input PDB file')
@click.option('--ofile', default='out_chain.pdb', help='Output PDB file name (default: out_chain.pdb)')
def command(pdb, ofile):
    """Convert segname to chainID in VMD."""
    
    tcl_script = f"""
mol new {pdb} type pdb
set all [atomselect top "all"]
set segnames [lsort -unique [$all get segname]]
foreach seg $segnames {{
        set selseg [atomselect top "segname $seg"]
        $selseg set chain [string index $seg 3]
}}
$all writepdb {ofile}
quit
"""
    
    script_name = "tmp_segid_to_chain.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD to convert segid to chain...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
    
    click.echo(f"Conversion finished! Output written to: {ofile}")
