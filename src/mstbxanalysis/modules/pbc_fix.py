import click
import MDAnalysis as mda
from MDAnalysis import transformations as trans
import warnings
import os

# Suppress warnings from MDAnalysis
warnings.filterwarnings('ignore')

class MOLTransformation:
    def __init__(self, top: str, traj: str, otraj: str, sel1: str, sel2: str, typeFix: str, method: str, stride=1):
        self.stride = stride
        self.top = top
        self.traj = traj
        self.otraj = otraj
        self.selPBC = sel1
        self.selOFile = sel2
        self.type = typeFix
        self.method = method
        if method != "vmd":
            self.u = mda.Universe(self.top, self.traj)

    def pbcFix(self):
        if self.method == "vmd":
            ext_top = os.path.splitext(self.top)[1][1:]
            ext_traj = os.path.splitext(self.traj)[1][1:]
            outname = os.path.splitext(self.otraj)[0] + "_noPBC" + os.path.splitext(self.otraj)[1]

            tcl_script = "pbc.tcl"
            with open(tcl_script, "w") as f:
                f.write("package require pbctools\n")
                f.write(f"mol new {self.top} type {ext_top}\n")
                f.write(f"mol addfile {self.traj} type {ext_traj} step {self.stride} waitfor all\n")

                click.echo(f"[INFO] Starting PBC fix from {self.type} using VMD.")
                f.write(f"pbc wrap -center com -centersel \"{self.selPBC}\" -all -compound res\n")
                f.write(f"set sel [atomselect top \"{self.selOFile}\"]\n")
                f.write(f"animate write {ext_traj} {outname} beg 0 end -1 waitfor all sel $sel\n")
                f.write("quit")
            
            os.system(f"vmd -dispdev text -e {tcl_script}")
            # os.remove(tcl_script) # Optional: remove script after use

        else:
            if self.type == "solution":
                click.echo("[INFO] Starting PBC fix from solution using MDAnalysis.")
                protein = self.u.select_atoms(self.selPBC)
                waters = self.u.select_atoms(f"not {self.selPBC}")
                workflow = [
                    trans.unwrap(protein, max_threads=4),
                    trans.center_in_box(protein, center="geometry", max_threads=4),
                    trans.wrap(waters, compound="residues", max_threads=4)
                ]
                self.u.trajectory.add_transformations(*workflow)
                click.echo("[INFO] Finish PBC fix from solution.")

            elif self.type == "membrane":
                click.echo("[INFO] Starting PBC fix from membrane using MDAnalysis.")
                protein = self.u.select_atoms(self.selPBC)
                ag = self.u.atoms
                workflow = [
                    trans.unwrap(ag),
                    trans.center_in_box(protein, center="mass"),
                    trans.wrap(ag, compound="fragment")
                ]
                self.u.trajectory.add_transformations(*workflow)
                click.echo("[INFO] Finish PBC fix from membrane.")

    def writeTRAJ(self, otraj, u):
        selAtoms = u.select_atoms(self.selOFile)
        with mda.Writer(otraj, selAtoms.n_atoms) as W:
            total = len(u.trajectory)
            for i, ts in enumerate(u.trajectory):
                W.write(selAtoms)
                if (i + 1) % 10 == 0 or (i + 1) == total:
                    click.echo(f"Write Frame [{i+1}/{total} - {(i+1)/total*100:.2f}%]")

    def fit(self, noPBC_traj):
        u1 = noPBC_traj
        ref_u1 = u1.copy()
        reference = ref_u1.select_atoms(self.selPBC)
        prot = u1.select_atoms(self.selPBC)

        if self.type == "solution":
            workflow = trans.fit_rot_trans(prot, reference)
            click.echo("[INFO] Fitting rot+trans complete for solution.")
        elif self.type == "membrane":
            workflow = trans.fit_rot_trans(prot, reference, plane='xy', weights="mass")
            click.echo("[INFO] Fitting membrane rotxy+transxy complete.")
        
        u1.trajectory.add_transformations(workflow)
        return u1

@click.command()
@click.option('--top', required=True, help='Topology file [TPR, PSF, etc.]')
@click.option('--itraj', required=True, help='Input trajectory file [XTC, DCD]')
@click.option('--sel-pbc', 'selPBC', default='protein', help='Selection for PBC centering.')
@click.option('--sel-ofile', 'selOFile', default='all', help='Selection for output trajectory.')
@click.option('--method', default='mda', type=click.Choice(['vmd', 'mda']), help='Method to use.')
@click.option('--steps', default=1, type=int, help='Slicing frame (stride), used in VMD.')
@click.option('--type', 'type_sys', default='solution', type=click.Choice(['solution', 'membrane']), help='System type.')
@click.option('--otraj', required=True, help='Output trajectory name.')
@click.option('--fit', is_flag=True, help='Enable rot+trans fitting.')
def command(top, itraj, selPBC, selOFile, method, steps, type_sys, otraj, fit):
    """Remove PBC effects and optionally fit trajectory."""
    
    name_noPBC = os.path.splitext(otraj)[0] + "_noPBC" + os.path.splitext(otraj)[1]
    name_fit = os.path.splitext(otraj)[0] + "_noPBC_fit" + os.path.splitext(otraj)[1]

    molt = MOLTransformation(top, itraj, otraj, selPBC, selOFile, type_sys, method, steps)
    molt.pbcFix()

    if method == "mda":
        molt.writeTRAJ(name_noPBC, molt.u)
        if fit:
            click.echo("[INFO] Starting fitting on MDAnalysis processed trajectory.")
            trajnoPBC = mda.Universe(top, name_noPBC, in_memory=True)
            u1 = molt.fit(trajnoPBC)
            molt.writeTRAJ(name_fit, u1)
    else:
        # VMD method already wrote name_noPBC (with _noPBC suffix if logic in pbcFix followed)
        # Note: the pbcFix in VMD mode currently determines its own outname.
        if fit:
            actual_no_pbc = os.path.splitext(otraj)[0] + "_noPBC" + os.path.splitext(otraj)[1]
            if not os.path.exists(actual_no_pbc):
                 # VMD script uses ext_traj as output format, check if it exists
                 click.echo(f"[WARNING] Expected {actual_no_pbc} not found. Fitting might fail if VMD didn't produce it.")
            
            click.echo("[INFO] Starting fitting on VMD processed trajectory.")
            trajnoPBC = mda.Universe(top, actual_no_pbc)
            trajnoPBC.transfer_to_memory()
            u1 = molt.fit(trajnoPBC)
            molt.writeTRAJ(name_fit, u1)
    
    click.echo("PBC fix and fitting complete.")
