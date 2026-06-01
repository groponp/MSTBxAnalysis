import click
import math
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable
import seaborn as sns
import warnings

warnings.filterwarnings("ignore")
sns.set()

def free_energy_surface(v1, v2, temperature, bins, ofile_name):
    kB = 3.2976268E-24 # cal/K
    An = 6.02214179E23
    T = float(temperature)

    V = np.zeros((bins, bins))
    DG = np.zeros((bins, bins))

    minv1, maxv1 = np.min(v1), np.max(v1)
    minv2, maxv2 = np.min(v2), np.max(v2)

    I1 = maxv1 - minv1
    I2 = maxv2 - minv2

    for i in range(len(v1)):
        for x in range(bins):
            if v1[i] <= minv1 + (x + 1) * I1 / bins and v1[i] > minv1 + x * I1 / bins:
                for y in range(bins):
                    if v2[i] <= minv2 + (y + 1) * I2 / bins and v2[i] > minv2 + y * I2 / bins:
                        V[x][y] += 1
                        break
                break

    P = V.flatten()
    Pmax = np.max(P)
    LnPmax = math.log(Pmax)

    dat_file = ofile_name.split('.')[0] + ".dat"
    with open(dat_file, 'w') as f:
        for x in range(bins):
            for y in range(bins):
                if V[x][y] == 0:
                    DG[x][y] = 10
                else:
                    DG[x][y] = -0.001 * An * kB * T * (math.log(V[x][y]) - LnPmax)
                
                x_val = (2 * minv1 + (2 * x + 1) * I1 / bins) / 2
                y_val = (2 * minv2 + (2 * y + 1) * I2 / bins) / 2
                f.write(f"{x_val}\t{y_val}\t{DG[x][y]}\n")
            f.write("\n")

    return DG

def plot_fel(v1, v2, dg, labels, ofile):
    z_l = r'$\Delta G$'+' [kcal/mol]'
    extent = [np.min(v2), np.max(v2), np.min(v1), np.max(v1)]

    fig, ax = plt.subplots(figsize=(3.5, 2.5))
    im = ax.matshow(dg, cmap='jet', extent=extent, origin='lower', interpolation='bilinear', aspect='auto')
    
    ax.tick_params(axis='both', labelsize=9)
    ax.set_xlabel(labels[0], fontsize=12)
    ax.set_ylabel(labels[1], fontsize=12)
    ax.xaxis.set_ticks_position('bottom')

    divider = make_axes_locatable(ax)
    cax = divider.append_axes("right", size="5%", pad=0.09)
    cbar = plt.colorbar(im, cax=cax)
    cbar.set_label(z_l, size=10)
    
    plt.savefig(ofile, dpi=300, bbox_inches='tight')
    click.echo(f"Plot saved to {ofile}")

@click.command()
@click.option('--file1', required=True, help='Collective variable 1 file [e.g. rgyr.dat]')
@click.option('--file2', required=True, help='Collective variable 2 file [e.g. rmsd.dat]')
@click.option('--temperature', default=310.0, help='Temperature in Kelvin')
@click.option('--bins', default=25, help='Number of bins')
@click.option('--x-label', default='RMSD [A]', help='X-axis label')
@click.option('--y-label', default='Rgyr [A]', help='Y-axis label')
@click.option('--ofile', default='FEL.png', help='Output plot name')
def command(file1, file2, temperature, bins, x_label, y_label, ofile):
    """Calculate Free Energy Landscape (FEL) from two collective variables."""
    click.echo(f"Reading data from {file1} and {file2}...")
    v1 = np.genfromtxt(file1, usecols=1, delimiter='\t', skip_header=1)
    v2 = np.genfromtxt(file2, usecols=1, delimiter='\t', skip_header=1)

    dg = free_energy_surface(v1, v2, temperature, bins, ofile)
    plot_fel(v1, v2, dg, [x_label, y_label], ofile)
    click.echo("FEL analysis complete!")
