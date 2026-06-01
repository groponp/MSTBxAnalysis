import click
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

@click.command()
@click.option('--flog', '-f', required=True, help='Log file from NAMD MD equilibration.')
@click.option('--plot', '-p', default=0, type=int, help='Binary 0 or 1. Where 0 is off and 1 is on, to generate plots.')
def command(flog, plot):
    """Extract Thermodynamics and Kinetics observables from NAMD equilibration logs."""
    
    pressavg = []
    tempavg = []
    volume = []
    temperature = []
    pressure = []
    kinetics = []
    frame = []
    etotal = []
    gpressure = []
    gpressavg = []

    if not os.path.exists(flog):
        click.echo(f"Error: Log file {flog} not found.")
        return

    # read file.
    with open(flog) as file:
        for line in file:
            if line.startswith("ENERGY") and float(line.split()[12]) != 0:  # avoid data from energy minimization.
                parts = line.split()
                frame.append(int(parts[1]))
                if float(parts[16]) != 0: pressure.append(float(parts[16]))
                if float(parts[12]) != 0: temperature.append(float(parts[12]))
                if float(parts[18]) != 0: volume.append(float(parts[18]))
                if float(parts[15]) != 0: tempavg.append(float(parts[15]))
                if float(parts[19]) != 0: pressavg.append(float(parts[19]))
                if float(parts[11]) != 0: etotal.append(float(parts[11]))
                if float(parts[17]) != 0: gpressure.append(float(parts[17]))
                if float(parts[20]) != 0: gpressavg.append(float(parts[20]))
                if float(parts[10]) != 0: kinetics.append(float(parts[10]))

    if not frame:
        click.echo("No energy data found in the log file.")
        return

    ns = [(float(i) * 0.002) / 1000 for i in frame]

    def mean(x):
        return np.average(x[1:]) if len(x) > 1 else np.nan

    def error(y):
        return np.std(y[1:]) / np.sqrt(len(y[1:])) if len(y) > 1 else np.nan

    def std(z):
        return np.std(z[1:]) if len(z) > 1 else np.nan

    click.echo("Average from Data:")
    click.echo("==========================")
    click.echo(f"Analysis   : from {frame[1] if len(frame)>1 else frame[0]} to {frame[-1]} timestep with n={len(frame)-1} data.")
    
    stats = [
        ("ETOTAL", etotal),
        ("KINETICS", kinetics),
        ("TEMP", temperature),
        ("TEMPAVG", tempavg),
        ("PRESS", pressure),
        ("PRESSAVG", pressavg),
        ("GPRESSURE", gpressure),
        ("GPRESSAVG", gpressavg),
        ("VOLUME", volume)
    ]

    for label, data in stats:
        if data:
            click.echo("{0:<10} : {1:.2f} error: {2:.2f} std: {3:.2f}".format(label, mean(data), error(data), std(data)))

    if plot == 1:
        observables = {
            "pressavg": pressavg, "tempavg": tempavg, "volume": volume, 
            "temperature": temperature, "pressure": pressure, "kinetics": kinetics, 
            "etotal": etotal, "gpressure": gpressure, "gpressavg": gpressavg
        }

        for name, obs in observables.items():
            if not obs: continue
            
            # Save CSV
            df = pd.DataFrame({"time": ns[:len(obs)], name: obs})
            df.to_csv(f"{name}.csv", index=False)
            click.echo(f"[INFO] Writing {name} data to {name}.csv")

            # Plotting
            fig, ax = plt.subplots()
            ax.plot(df["time"][::10], df[name][::10], linewidth=0.5, color="black")

            minit, maxit = df["time"].min(), df["time"].max()
            minip, maxip = df[name].min(), df[name].max()

            ax.set(xlabel="time/ns", ylabel=name)
            ax.set_xlim(minit, maxit)
            ax.set_ylim(minip, maxip)
            ax.ticklabel_format(style='plain', useOffset=False)

            fig.set_size_inches(9, 5)
            fig.tight_layout()
            plt.savefig(f"{name}.png")
            plt.close(fig)
            click.echo(f"[INFO] Plot saved to {name}.png")

    click.echo("NAMDStats analysis done.")
