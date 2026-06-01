import click
import subprocess

@click.command()
@click.option('--dcd', required=True, help='Trajectory file in DCD format.')
@click.option('--pdb', required=True, help='PDB file with coordinates.')
@click.option('--n-modes', default=10, help='Number of modes to calculate.')
@click.option('--selection', default='protein and same residue as within 4 of resname LIG', help='Atom selection string.')
@click.option('--prefix', default='pdb_pca', help='Output prefix.')
def command(dcd, pdb, n_modes, selection, prefix):
    """
    Run Essential Dynamics Analysis (EDA/PCA) using ProDy.
    """
    click.echo("Running EDA...")
    cmd = [
        "prody", "eda", dcd, "--pdb", pdb,
        "-n", str(n_modes),
        "-s", selection,
        "-p", prefix,
        "-A",
        "-F", "pdf",
        "-d", "800"
    ]
    subprocess.run(cmd, check=True)
    click.echo("EDA finished.")

if __name__ == '__main__':
    command()
