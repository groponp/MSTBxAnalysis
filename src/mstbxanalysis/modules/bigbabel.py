import click
import os
import glob
import time
import pandas as pd
import numpy as np
from openbabel import pybel

def search_abspath(directory):
    abspath = os.path.abspath(directory)
    click.echo(f"The Path is: {abspath}")
    return abspath

def read_and_split_sdf(path, molregex="*.sdf"):
    db_list = glob.glob(os.path.join(path, molregex))
    count = 0
    for database in db_list:
        base_name = os.path.basename(database).split(".")[0]
        dirname = os.path.join(path, f"tmp_{base_name}")
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        
        for sdf in pybel.readfile("sdf", database):
            save_path = os.path.join(dirname, f"L{count}.smi")
            sdf.write("smi", save_path, overwrite=True)
            count += 1
            if count % 100 == 0:
                click.echo(f"Mol#{count} converted to {save_path}")
    return count

def make_dataframe_and_save(path, subdir_regex="tmp_*", remove_smi_db=True):
    names = []
    smiles = []
    fromdb = []

    subdirs = glob.glob(os.path.join(path, subdir_regex))
    for subdir in subdirs:
        if os.path.isdir(subdir):
            smiles_list = glob.glob(os.path.join(subdir, "*.smi"))
            for smile_file in smiles_list:
                name = os.path.basename(smile_file).split(".")[0]
                names.append(str(name))
                with open(smile_file) as f:
                    lines = f.read().strip()
                    smi = lines.split()[0] if lines.split() else ""
                    smiles.append(str(smi))
                    fromdb.append(os.path.basename(subdir))
            
            if remove_smi_db:
                import shutil
                shutil.rmtree(subdir)
                click.echo(f"[INFO] Removed temporary directory {subdir}")

    df0 = pd.DataFrame({"Mol_Name": names, "Smiles": smiles, "DataBase": fromdb})
    df0.to_csv('BigDatabase_full.csv', index=False)
    
    # Save in batches of 500 for SMI
    batch_size = 500
    for i in range(0, len(df0), batch_size):
        batch = df0.iloc[i:i+batch_size][["Smiles", "Mol_Name"]]
        batch.to_csv(f'BigDatabase_{i+batch_size}.smi', index=False, sep="\t", header=False)
    
    return len(df0)

def convert_smi_to_pdb(path, db, odir, gypsum_path, minpH=7.4, maxpH=7.4, pka=0, maxconf=5, numproc=8):
    if not os.path.exists(odir):
        os.makedirs(os.path.join(path, odir))
    
    if os.path.getsize(db) == 0:
        click.echo(f"File {db} has no smile data")
        return

    command = (f"python {gypsum_path}/run_gypsum_dl.py --source {db} --min_ph {minpH} --max_ph {maxpH} "
               f"--pka_precision {pka} --max_variants_per_compound {maxconf} --output_folder {odir} --add_pdb_output "
               f"--separate_output_files --use_durrant_lab_filters --job_manager multiprocessing "
               f"--num_processors {numproc}")
    
    click.echo(f"Running Gypsum-DL: {command}")
    os.system(command)
    # Cleanup SDFs if any
    for sdf in glob.glob(os.path.join(odir, "*.sdf")):
        os.remove(sdf)

def convert_ligand_to_pdbqt(directory, pythonsh, prepare_ligand, ligregex="*.pdb"):
    workdir = os.getcwd()
    pdbs = glob.glob(os.path.join(workdir, directory, ligregex))
    out_dir = os.path.join(workdir, "ligand_pdbqt")
    
    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    for pdb in pdbs:
        if os.path.getsize(pdb) > 0:
            name = os.path.basename(pdb).split(".")[0]
            cmd = f"{pythonsh} {prepare_ligand} -v -l {pdb} -o {out_dir}/{name}.pdbqt"
            os.system(cmd)
        else:
            click.echo(f"No data in {pdb}")

@click.command()
@click.option('--dir', 'directory', required=True, help='Directory containing SDF files.')
@click.option('--molregex', default='*.sdf', help='Regex to match SDF files.')
@click.option('--gypsum', envvar='GYPSUM', help='Path to Gypsum-DL directory.')
@click.option('--pythonsh', help='Path to ADT pythonsh.')
@click.option('--prepare-ligand', help='Path to ADT prepare_ligand4.py.')
@click.option('--min-ph', default=7.4, type=float, help='Min pH for ionization.')
@click.option('--max-ph', default=7.4, type=float, help='Max pH for ionization.')
@click.option('--numproc', default=4, type=int, help='Number of processors.')
@click.option('--skip-split', is_flag=True, help='Skip SDF splitting.')
@click.option('--skip-pdb', is_flag=True, help='Skip SMI to PDB conversion.')
@click.option('--skip-pdbqt', is_flag=True, help='Skip PDB to PDBQT conversion.')
def command(directory, molregex, gypsum, pythonsh, prepare_ligand, min_ph, max_ph, numproc, skip_split, skip_pdb, skip_pdbqt):
    """Process large databases of ligands from SDF to PDBQT."""
    
    path = search_abspath(directory)
    os.chdir(path)
    
    if not skip_split:
        click.echo("Splitting SDF files...")
        read_and_split_sdf(path, molregex)
        make_dataframe_and_save(path)

    if not skip_pdb:
        if not gypsum:
            click.echo("Error: Gypsum-DL path not provided (use --gypsum or GYPSUM env var).")
        else:
            click.echo("Converting SMI to PDB using Gypsum-DL...")
            smi_files = glob.glob("*.smi")
            for smi in smi_files:
                convert_smi_to_pdb(path, smi, "ligand_pdb", gypsum, minpH=min_ph, maxpH=max_ph, numproc=numproc)
                # os.remove(smi) # Optional cleanup

    if not skip_pdbqt:
        if not pythonsh or not prepare_ligand:
            click.echo("Error: AutoDockTools paths (pythonsh and prepare_ligand4.py) not provided.")
        else:
            click.echo("Converting PDB to PDBQT...")
            convert_ligand_to_pdbqt("ligand_pdb", pythonsh, prepare_ligand)

    click.echo("BigBabel processing complete.")
