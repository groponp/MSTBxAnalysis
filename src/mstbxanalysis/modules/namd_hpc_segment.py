import click
import subprocess
import os
import glob
import re

@click.command()
@click.option('--cpus', default=20, help='Number of CPUs per task.')
@click.option('--steps-initial', default=500000000, help='Total initial steps.')
@click.option('--save-each', default=2.0, help='Time in ns for each segment.')
@click.option('--eq-dir', default='04_eq_gamd', help='Equilibrium directory.')
@click.option('--prod-dir', default='05_gamd', help='Production directory.')
def command(cpus, steps_initial, save_each, eq_dir, prod_dir):
    """
    Perform segment MD on HPC with NAMD.
    Automates Equilibrium and Production GaMD segments.
    """
    click.echo("Starting Segmented MD management...")

    # EQ-GamD
    if os.path.exists(eq_dir):
        os.chdir(eq_dir)
        state_files = glob.glob("*.state")
        if not state_files:
            click.echo("Running EQ-GamD...")
            subprocess.run(["namd2", f"+p{cpus}", "+devices", "0", "+idlepoll", "md_eq_gamd.namd"], 
                           stdout=open("md_eq_gamd.out", "w"), check=True)
            
            # Copy restart files to production directory
            os.makedirs(f"../{prod_dir}", exist_ok=True)
            for f in ["gamd-eq-wrap.restart.coor", "gamd-eq-wrap.restart.xsc", 
                      "gamd-eq-wrap.restart.gamd", "gamd-eq-wrap.colvars.state"]:
                if os.path.exists(f):
                    shutil_copy(f, f"../{prod_dir}/")
        os.chdir("..")

    # Production-GamD
    if os.path.exists(prod_dir):
        os.chdir(prod_dir)
        dcd_files = glob.glob("*.dcd")
        count_dcd = len(dcd_files)
        out_files = glob.glob("prod_*.out")
        count_out = len(out_files)

        if count_dcd == 0:
            start_md = 1
            # Update prod.namd for first run
            update_namd_file("prod.namd", [
                (f"md_{count_out}", "omd"),
                (f"md_{count_out-1}", "gamd-eq-wrap"),
                ("set restart_inicial 0", "set restart_inicial 1"),
                ("set restart_continuar 1", "set restart_continuar 0")
            ])
        else:
            update_namd_file("prod.namd", [
                (f"md_{count_out}", f"md_{count_dcd}"),
                (f"md_{count_out-1}", f"md_{count_dcd-1}")
            ])
            click.echo(f"Resuming production from segment {count_dcd}...")
            subprocess.run(["namd2", f"+p{cpus}", "+devices", "0", "+idlepoll", "prod.namd"],
                           stdout=open(f"prod_{count_dcd}.out", "w"), check=True)
            start_md = count_dcd + 1

        # Calculate iterations
        dt = get_namd_param("prod.namd", "timestep")
        if dt is None:
            click.echo("Error: timestep not found in prod.namd")
            return
        dt = float(dt) / 1000.0 # to ps
        
        time_ns = steps_initial * dt / 1000.0
        n_iterations = int(time_ns / save_each)
        namd_steps = int(save_each * 1000.0 / dt)

        click.echo(f"Time in ns: {time_ns:.3f}")
        click.echo(f"Number of iterations: {n_iterations}")

        # Set steps in namd file
        orig_steps = get_namd_param("prod.namd", "run")
        update_namd_file("prod.namd", [(orig_steps, str(namd_steps))])

        # Loop through segments
        while start_md <= n_iterations:
            prev_i = start_md - 1
            click.echo(f"Running segment {start_md} of {n_iterations}...")
            
            if start_md == 1:
                update_namd_file("prod.namd", [("omd", f"md_{start_md}")])
            elif start_md == 2:
                update_namd_file("prod.namd", [
                    (f"md_{prev_i}", f"md_{start_md}"),
                    ("gamd-eq-wrap", f"md_{prev_i}"),
                    ("set restart_inicial 1", "set restart_inicial 0"),
                    ("set restart_continuar 0", "set restart_continuar 1")
                ])
            else:
                update_namd_file("prod.namd", [
                    (f"md_{prev_i}", f"md_{start_md}"),
                    (f"md_{start_md-2}", f"md_{start_md-1}")
                ])
            
            subprocess.run(["namd2", f"+p{cpus}", "+devices", "0", "+idlepoll", "prod.namd"],
                           stdout=open(f"prod_{start_md}.out", "w"), check=True)
            start_md += 1

        os.chdir("..")

def update_namd_file(filename, replacements):
    with open(filename, 'r') as f:
        content = f.read()
    for old, new in replacements:
        content = content.replace(old, new)
    with open(filename, 'w') as f:
        f.write(content)

def get_namd_param(filename, param):
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if parts[0].lower() == param.lower():
                return parts[1]
    return None

if __name__ == '__main__':
    command()
turn parts[1]
    return None

if __name__ == '__main__':
    command()
    command()
