import click
import subprocess
import os
import glob

@click.command()
@click.option('--pattern', default='*.sdf', help='Pattern to match SDF files.')
@click.option('--ph', default=7.4, help='pH for protonation.')
def command(pattern, ph):
    """
    Batch convert SDF files to PDB using OpenBabel.
    Generates 3D coordinates and adds hydrogens at specific pH.
    """
    files = glob.glob(pattern)
    if not files:
        click.echo(f"No files matching {pattern} found.")
        return

    for f in files:
        base = os.path.splitext(f)[0]
        click.echo(f"Processing {f}...")
        os.makedirs(base, exist_ok=True)
        out_pdb = os.path.join(base, "out.pdb")
        
        cmd = ["babel", "-isdf", f, "-opdb", out_pdb, "--gen3D", "-p", str(ph)]
        subprocess.run(cmd, check=True)
    
    click.echo("Batch conversion finished.")

if __name__ == '__main__':
    command()
