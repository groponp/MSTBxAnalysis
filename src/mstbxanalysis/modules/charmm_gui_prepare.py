import click
import os
import subprocess

@click.command()
@click.option('--pdb', required=True, help='Input PDB file to fix')
@click.option('--lig-sel', default='resname UNL', help='Selection for the ligand (PyMOL syntax)')
@click.option('--opdb', default='complex_fix.pdb', help='Output fixed complex PDB')
@click.option('--olig', default='lig_fix.mol2', help='Output fixed ligand MOL2')
def command(pdb, lig_sel, opdb, olig):
    """Prepare PDB and MOL2 files for CHARMM-GUI inputs using PyMOL and OpenBabel."""
    
    pymol_script = f"""
from pymol import cmd
cmd.load('{pdb}')
cmd.remove('hydro')
cmd.select('lig', '{lig_sel}')
cmd.alter('lig', 'chain="Z"')
cmd.h_add('chain Z')

cmd.save('tmp_lig.mol2', 'chain Z')
cmd.save('tmp_complex.pdb', 'all')
exit
"""
    
    with open("tmp_prep.py", "w") as f:
        f.write(pymol_script)
        
    click.echo("Running PyMOL for structure preparation...")
    try:
        subprocess.run(["pymol", "-cq", "tmp_prep.py"], check=True)
        
        # Post-processing with sed
        click.echo("Applying fixes with sed...")
        os.system(f"sed 's/UNL/LIG/g' tmp_complex.pdb > {opdb}")
        os.system(f"sed 's/UNL1/LIG/g' tmp_lig.mol2 > tmp1.mol2")
        os.system(f"sed 's/UNL/LIG/g' tmp1.mol2 > tmp2.mol2")
        # Fixed logic for sed based on legacy script
        os.system(f"sed '3 s/CH.*/LIG/g' tmp2.mol2 > {olig}")
        
        click.echo(f"Files saved to: {opdb} and {olig}")
        
    except FileNotFoundError:
        click.echo("Error: 'pymol' command not found. Please ensure PyMOL is installed.")
    finally:
        for tmp in ["tmp_prep.py", "tmp_lig.mol2", "tmp_complex.pdb", "tmp1.mol2", "tmp2.mol2"]:
            if os.path.exists(tmp):
                os.remove(tmp)
                
    click.echo("Preparation finished!")
