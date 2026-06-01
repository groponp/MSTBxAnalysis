import click
import subprocess
import os
import glob
import shutil

@click.command()
@click.option('--smi', 'smi_file', required=True, help='Input SMILES file (one per line).')
@click.option('--config', 'config_file', required=True, help='Vina configuration file.')
@click.option('--cpu', default=4, help='Number of CPUs for Vina.')
@click.option('--force-field', default='MMFF94', help='Force field for minimization.')
@click.option('--ph', default=7.4, help='pH for protonation.')
def command(smi_file, config_file, cpu, force_field, ph):
    """
    Perform virtual screening with Autodock Vina.
    Includes SMILES splitting, geometry optimization, and docking.
    """
    if not os.path.exists(smi_file):
        click.echo(f"Error: SMILES file {smi_file} not found.")
        return

    if not os.path.exists(config_file):
        click.echo(f"Error: Config file {config_file} not found.")
        return

    # Step 0: Split smi file
    click.echo("Splitting SMILES file...")
    with open(smi_file, 'r') as f:
        lines = f.readlines()
    
    for i, line in enumerate(lines):
        lig_name = f"ligando_{i+1}"
        with open(lig_name, 'w') as f_out:
            f_out.write(line.strip())

    # Step 1: Conversion and Geometry Optimization
    lig_files = glob.glob("ligando_*")
    for lig in lig_files:
        sdf = f"{lig}.sdf"
        pdb = f"{lig}.pdb"
        pdbqt = f"{lig}.pdbqt"
        min_pdbqt = f"{lig}_min.pdbqt"

        click.echo(f"Processing {lig}: SMI -> SDF (2D)")
        subprocess.run(["babel", "-ismi", lig, "-osdf", sdf, "--gen2D"], check=True)
        
        click.echo(f"Processing {lig}: SDF -> PDB (3D, pH {ph})")
        subprocess.run(["babel", "-isdf", sdf, "-opdb", pdb, "--gen3D", "-p", str(ph)], check=True)
        
        click.echo(f"Processing {lig}: PDB -> PDBQT")
        subprocess.run(["babel", "-ipdb", pdb, "-opdbqt", pdbqt], check=True)
        
        click.echo(f"Minimizing {lig} with {force_field}...")
        with open(min_pdbqt, 'w') as f_min:
            subprocess.run(["obminimize", "-ff", force_field, "-n", "10000", "-sd", "-c", "1e-9", pdbqt], stdout=f_min, check=True)

    # Cleanup and move minimized ligands
    os.makedirs("ligands", exist_ok=True)
    for f in glob.glob("*_min.pdbqt"):
        shutil.move(f, os.path.join("ligands", f))
    
    # Remove intermediate files
    for f in glob.glob("ligando_*"):
        if os.path.isfile(f):
            os.remove(f)
    for f in glob.glob("*.sdf"):
        os.remove(f)
    for f in glob.glob("*.pdb"):
        os.remove(f)
    for f in glob.glob("*.pdbqt"):
        os.remove(f)

    # Step 2: Vina Screening
    click.echo("Starting Vina screening...")
    summary_lines = []
    min_ligands = glob.glob("ligands/*.pdbqt")
    
    for lig_path in min_ligands:
        name = os.path.basename(lig_path).replace("_min.pdbqt", "")
        out_pdbqt = f"{name}.pdbqt"
        log_file = f"{name}.log"
        
        click.echo(f"Docking {name}...")
        subprocess.run(["vina", "--config", config_file, "--ligand", lig_path, "--out", out_pdbqt, "--log", log_file, "--cpu", str(cpu)], check=True)
        
        # Extract best energy from log
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                capture = False
                for line in f:
                    if line.startswith("-------"):
                        capture = True
                        continue
                    if capture:
                        parts = line.split()
                        if len(parts) >= 2:
                            energy = parts[1]
                            summary_lines.append(f"{log_file} {energy}")
                        break

    # Sort summary
    summary_lines.sort(key=lambda x: float(x.split()[1]))
    with open("summary_sorted.txt", "w") as f:
        for line in summary_lines:
            f.write(line + "\n")

    # Step 3: Cleanup and convert results
    os.makedirs("result", exist_ok=True)
    for f in glob.glob("*.log"):
        shutil.move(f, "result/")
    for f in glob.glob("ligando_*.pdbqt"):
        # Convert pdbqt to pdb (crude way as in original script: cut -c-66)
        pdb_out = os.path.join("result", f.replace(".pdbqt", ".pdb"))
        with open(f, 'r') as f_in, open(pdb_out, 'w') as f_out:
            for line in f_in:
                f_out.write(line[:66] + "\n")
        os.remove(f)

    click.echo("Virtual screening finished. Check summary_sorted.txt for results.")

if __name__ == '__main__':
    command()
