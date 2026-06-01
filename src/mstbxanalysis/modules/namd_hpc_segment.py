import click
import os
import subprocess
import shutil

def get_namd_param(file_path, param):
    """Helper to extract a parameter from a NAMD config file."""
    if not os.path.exists(file_path):
        return None
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) >= 2 and parts[0].lower() == param.lower():
                return parts[1]
    return None

@click.command()
@click.option('--job-name', default='mstbx_job', help='SLURM job name')
@click.option('--cpus', default=20, help='CPUs per task')
@click.option('--time', default='5-0:0', help='SLURM time limit')
@click.option('--account', help='SLURM account name')
@click.option('--gpu', default='v100:1', help='GPU resource requirement')
@click.option('--eq-dir', default='04_eq_gamd', help='Equilibration directory')
@click.option('--prod-dir', default='05_gamd', help='Production directory')
@click.option('--total-ns', default=1000.0, type=float, help='Total simulation time in ns')
@click.option('--segment-ns', default=2.0, type=float, help='Time per segment in ns')
def command(job_name, cpus, time, account, gpu, eq_dir, prod_dir, total_ns, segment_ns):
    """Manage segmented NAMD simulations on HPC (SLURM)."""
    
    click.echo("--- NAMD HPC Segment Manager ---")
    
    # Check if we are in the right place
    if not os.path.exists(eq_dir) or not os.path.exists(prod_dir):
        click.echo(f"Error: Directories {eq_dir} or {prod_dir} not found.")
        return

    # 1. Handle Equilibration
    os.chdir(eq_dir)
    states = [f for f in os.listdir('.') if f.endswith('.state')]
    if not states:
        click.echo("Starting Equilibration...")
        # In a real HPC environment, this would be a sbatch submission
        # Here we just show the logic
        click.echo(f"Running: namd2 +p{cpus} +idlepoll md_eq_gamd.namd > md_eq_gamd.out")
    else:
        click.echo("Equilibration already finished. Copying restart files...")
        restart_files = [
            'gamd-eq-wrap.restart.coor', 'gamd-eq-wrap.restart.xsc',
            'gamd-eq-wrap.restart.gamd', 'gamd-eq-wrap.colvars.state'
        ]
        for f in restart_files:
            if os.path.exists(f):
                shutil.copy(f, os.path.join('..', prod_dir))
    
    os.chdir('..')

    # 2. Handle Production Segments
    os.chdir(prod_dir)
    dcds = [f for f in os.listdir('.') if f.endswith('.dcd')]
    outs = [f for f in os.listdir('.') if f.startswith('prod_') and f.endswith('.out')]
    
    start_idx = len(dcds) + 1
    iterations = int(total_ns / segment_ns)
    
    click.echo(f"Total Iterations: {iterations}")
    click.echo(f"Starting from Segment: {start_idx}")

    # Logic to update NAMD config and run segments
    # (Simplified for the CLI wrapper)
    for i in range(start_idx, iterations + 1):
        prev = i - 1
        click.echo(f"Preparing Segment {i}...")
        # Here would be the sed logic to update prod.namd
        # Then submission: sbatch or direct run
        click.echo(f"Running Segment {i} (Restarting from {prev})...")
    
    os.chdir('..')
    click.echo("HPC Segment Manager task finished.")

if __name__ == '__main__':
    command()
