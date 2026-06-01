import click
import subprocess
import os
import glob

@click.command()
@click.option('--ligands', default='ligando_*.pdbqt', help='Pattern for ligand files.')
@click.option('--config', default='config.text', help='Vina configuration file.')
@click.option('--vina-exe', default='vina', help='Path to vina executable.')
def command(ligands, config, vina_exe):
    """
    Automated virtual screening using Autodock Vina.
    Loops over ligands matching the pattern.
    """
    files = glob.glob(ligands)
    if not files:
        click.echo(f"No ligands matching {ligands} found.")
        return

    if not os.path.exists(config):
        click.echo(f"Config file {config} not found.")
        return

    for f in files:
        base = os.path.splitext(f)[0]
        click.echo(f"Processing ligand {base}...")
        os.makedirs(base, exist_ok=True)
        
        out_pdbqt = os.path.join(base, "ligand_output.pdbqt")
        log_file = os.path.join(base, "log.text")
        
        cmd = [vina_exe, "--config", config, "--ligand", f, "--out", out_pdbqt, "--log", log_file]
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            click.echo(f"Error docking {f}: {e}")

    click.echo("Virtual screening loop finished.")

if __name__ == '__main__':
    command()
