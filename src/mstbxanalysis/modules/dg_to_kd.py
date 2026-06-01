import click
import math

@click.command()
@click.option('--be', '--binding-energy', required=True, type=float, help='Binding energy from Docking in kcal/mol')
@click.option('--conc', required=True, type=click.Choice(['M', 'mM', 'nM']), help='Concentration unit of Kd')
@click.option('-o', '--out-name', help='Name of the output file')
def command(be, conc, out_name):
    """Calculate Dissociation Constant (Kd) from Binding Gibbs Free Energy (ΔG)."""
    # Math Algorithm
    # R = 1.98 cal/(mol*K), T = 298.15 K
    kd = math.exp((be * 1000) / (1.98 * 298.15))
    
    unit_factor = {
        'M': 1.0,
        'mM': 1e6,
        'nM': 1e9
    }
    
    kd_final = kd * unit_factor[conc]
    
    click.echo(f"Binding Energy: {be} kcal/mol")
    click.echo(f"Calculated Kd: {kd_final:.4e} {conc}")
    
    if out_name:
        with open(out_name, "a") as f:
            f.write(f"{kd_final}\t{conc}\n")
        click.echo(f"Result appended to {out_name}")
