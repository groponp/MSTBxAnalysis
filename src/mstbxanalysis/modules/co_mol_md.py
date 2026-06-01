import click
import numpy as np
import pandas as pd

@click.command()
@click.option('--conc', '-c', required=True, type=float, help='Concentration in mol/L.')
@click.option('--vol', '-b', required=True, type=float, help='Box volume in A^3.')
@click.option('--ofile', '-o', default='num_molecules.txt', help='Output file name.')
def command(conc, vol, ofile):
    """Calculate ligand concentration for Flooding MD."""
    
    # Avogadro constant
    avogadro = 6.02214076e23
    # Conversion factor from Angstrom^3 to Litre: 1 A^3 = 1e-27 L
    conversion_factor = 1e-27
    
    # num_mol = (vol * conversion_factor) * conc * avogadro
    num_mol = vol * conc * avogadro * conversion_factor

    result_str = (
        f"Number of molecules: {num_mol:.4f} molecules (round as needed)\n"
        f"Concentration used: {conc} mol/L\n"
        f"Box volume used: {vol} A^3\n"
    )
    
    with open(ofile, 'w') as f:
        f.write(result_str)

    click.echo(result_str)
    click.echo(f"Results written to {ofile}")
