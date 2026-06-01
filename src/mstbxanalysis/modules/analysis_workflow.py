import click
import subprocess
import os
import glob

@click.command()
@click.option('--dirs', default='C*', help='Pattern for directories to analyze.')
@click.option('--coord', default='system_fix_domain.pdb', help='Coordinate file name.')
@click.option('--traj', default='md_0_200_noPBC.xtc', help='Trajectory file name.')
@click.option('--temp', default=310.0, help='Temperature for FEL.')
def command(dirs, coord, traj, temp):
    """
    General analysis workflow for MD simulations.
    Iterates over directories and runs multiple analyses:
    RMSD, RMSF, 2Dmatrix, Rgyr, SASA, and FEL.
    """
    target_dirs = glob.glob(dirs)
    if not target_dirs:
        click.echo(f"No directories matching {dirs} found.")
        return

    # Selections from original script
    selections = [
        ("protein and name CA", "prot"),
        ("segid KIN and name CA", "kin"),
        ("segid ROC and name CA", "roc"),
        ("segid COR and name CA", "cor"),
        ("resname LIG and not name H", "LIG"),
        ("resname ATP and not name H", "ATP"),
        ("resname GDP and not name H", "GDP")
    ]

    for d in target_dirs:
        if not os.path.isdir(d):
            continue
        
        click.echo(f"Processing directory: {d}")
        os.chdir(d)

        # 1. RMSD
        click.echo("Running RMSD...")
        for sel, label in selections:
            subprocess.run(["mstbxanalysis", "rmsd", f"--coord={coord}", f"--traj={traj}", f"--sel={sel}", f"--ofile=rmsd_{label}.dat"])

        # 2. RMSF
        click.echo("Running RMSF...")
        for sel, label in selections:
            if "resname" not in sel: # Original script only did protein/segments for RMSF
                 subprocess.run(["mstbxanalysis", "mda-rmsf", f"--coord={coord}", f"--traj={traj}", f"--sel={sel}", f"--ofile=rmsf_{label}.dat"])

        # 3. 2D Matrix
        click.echo("Running 2Dmatrix...")
        for sel, label in selections:
            subprocess.run(["mstbxanalysis", "mda-2dmatrix", f"--coord={coord}", f"--traj={traj}", f"--sel={sel}", f"--ofile=2Dmatrix_{label}.svg"])

        # 4. Rgyr
        click.echo("Running Rgyr...")
        for sel, label in selections:
            subprocess.run(["mstbxanalysis", "mda-rgyr", f"--coord={coord}", f"--traj={traj}", f"--sel={sel}", f"--ofile=rgyr_{label}.dat"])

        # 5. SASA
        click.echo("Running SASA...")
        sasa_selections = [
            ("protein and same residue as within 5 of resname LIG", "prot_LIG"),
            ("protein and same residue as within 5 of resname ATP", "prot_ATP"),
            ("protein and same residue as within 5 of resname GDP", "prot_GDP")
        ]
        for sel, label in sasa_selections:
             subprocess.run(["mstbxanalysis", "vmd-sasa", f"--coord={coord}", f"--traj={traj}", f"--sel1={sel}", f"--sel2={sel}", f"--ofile=sasa_{label}.dat"])

        # 6. FEL
        click.echo("Running FEL...")
        fel_configs = [
            ("rgyr_LIG.dat", "rmsd_LIG.dat", "FEL_LIG.svg"),
            ("rgyr_ATP.dat", "rmsd_ATP.dat", "FEL_ATP.svg"),
            ("rgyr_GDP.dat", "rmsd_GDP.dat", "FEL_GDP.svg")
        ]
        for f1, f2, ofile in fel_configs:
            if os.path.exists(f1) and os.path.exists(f2):
                subprocess.run(["mstbxanalysis", "fel", f"--file1={f1}", f"--file2={f2}", f"--temperature={temp}", "--bin=25", f"--ofile={ofile}"])

        os.chdir("..")

    click.echo("Workflow finished.")

if __name__ == '__main__':
    command()
