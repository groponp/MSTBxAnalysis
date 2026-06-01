import click
import os

class IO:
    @staticmethod
    def message(string, tm="INFO"):
        if tm == "INFO":
            click.echo(f"[INFO    ] {string}")
        elif tm == "WARNING":
            click.echo(f"[WARNING ] {string}")
        else:
            click.echo(f"[ERROR   ] {string}")

class Solution:
    def __init__(self, iPDB, oGRO, water_model, ff):
        self.iPDB = iPDB
        self.oGRO = oGRO
        self.water_model = water_model
        self.ff = ff

    def pdb2gmx(self):
        IO.message("Running pdb2gmx", tm="INFO")
        # The legacy script only had os.system("gmx")
        # In a real scenario, this would be a full gmx pdb2gmx command.
        command = f"gmx pdb2gmx -f {self.iPDB} -o {self.oGRO} -water {self.water_model} -ff {self.ff}"
        click.echo(f"Executing: {command}")
        os.system(command)

@click.command()
@click.option('--ipdb', required=True, help='Input PDB file.')
@click.option('--ogro', default='system.gro', help='Output GRO file.')
@click.option('--water', default='tip3p', help='Water model.')
@click.option('--ff', default='amber99sb-ildn', help='Force field.')
def command(ipdb, ogro, water, ff):
    """Perform High-Throughput MD setup (Simplified wrapper)."""
    sol = Solution(ipdb, ogro, water, ff)
    sol.pdb2gmx()
    click.echo("Setup finished.")
