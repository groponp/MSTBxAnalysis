# MSTBxAnalysis

**Version:** 0.5.0-beta

Modular analysis tools for computational biophysics and biology. This project is a refactored and modernized version of the `CompBiology-Biophysics` script collection, designed for ease of use and extensibility.

## Features
- **Modular CLI:** Use a single command `mstbxanalysis` to access all tools.
- **Robust Loading:** The CLI handles missing dependencies gracefully, loading only available modules.
- **Easy Installation:** Install via `pip` or set up a dedicated `conda` environment.
- **Extensible Architecture:** Adding a new analysis script is as simple as dropping a Python file into the `modules/` directory.
- **Cross-Platform:** Compatible with Linux and macOS.

## Installation

### Using Pip (Recommended)
From the root of the repository:
```bash
pip install -e .
```
*Note: Using `-e` (editable mode) installs the package as a symbolic link to your source code. This means any changes you make to the files in `src/` will be immediately available in the `mstbxanalysis` command without needing to re-install. It also ensures all dependencies are correctly resolved.*

### Core Libraries and Recommendations

This project is primarily built using **MDAnalysis** and **VMD's Tcl script interpreter**. We strongly suggest that developers and contributors prioritize these libraries when adding new functionality. Please attempt to implement new analysis tools using these established methods before introducing additional dependencies.

## Usage

The general syntax is:
```bash
mstbxanalysis [COMMAND] [OPTIONS]
```

### Available Commands

#### Core MDAnalysis Tools
- **`rmsd`**: Calculate Root Mean Square Deviation (RMSD).
- **`mda-rgyr`**: Calculate Radius of Gyration (Rgyr).
- **`mda-rmsf`**: Calculate Root Mean Square Fluctuation (RMSF).
- **`mda-2dmatrix`**: Calculate and plot a 2D RMSD Distance Matrix.
- **`mda-convert-traj`**: Convert coordinates and trajectories between different formats.
- **`pbc-fix`**: Remove PBC effects and fit trajectories using MDAnalysis or VMD.

#### VMD-based Tools
- **`vmd-sasa`**: Calculate Surface Accessible Solvent Area (SASA).
- **`vmd-get-box`**: Calculate center and box size for docking (AutoDock/Vina).
- **`vmd-pbc-wrap`**: PBC wrapping and alignment using VMD/pbctools.
- **`vmd-rmsd-residue`**: Calculate average RMSD per residue and store in PDB beta column.
- **`vmd-segid-to-chain`**: Convert VMD segnames to chainIDs.
- **`vmd-merge-pdb`**: Merge multiple PDB files into a single system.
- **`vmd-reduce-traj`**: Reduce trajectory size by skipping frames.
- **`vmd-movie-render`**: Render movies from VMD scenes.
- **`vmd-molpack`**: Build biomolecular systems (orient, topology, solvate, ionize).
- **`vmd-molywood`**: Automate Molywood movie generation.
- **`vmd-make-segname`**: Set segment names for protein regions.
- **`vmd-jarzynski`**: Setup Jarzynski equality pulling scripts.
- **`vmd-make-tclforces`**: Mark PDB files for TclForces/TclBC.
- **`orient-z`**: Orient protein along the Z-axis using VMD.
- **`remove-rot-trans`**: Remove rotation and translation using VMD.

#### Simulation Prep & Building
- **`bigbabel`**: Process ligand databases (SDF split -> SMI -> PDB -> PDBQT).
- **`charmm-gui-prepare`**: Prepare PDB/MOL2 for CHARMM-GUI inputs.
- **`co-mol-md`**: Calculate ligand counts for concentration-based flooding.
- **`gmx-atom-index`**: Create or append to GROMACS index files (.ndx).
- **`make-flooding`**: Generate Packmol inputs for flooding MD.
- **`namd-to-charmm`**: Convert NAMD formats (PSF/PDB) to CHARMM.
- **`namd-to-gmx`**: Convert NAMD formats (PSF/PDB) to GROMACS.
- **`sdf-to-pdb`**: Batch convert SDF libraries to PDB with 3D coordinates.

#### Statistical & Thermodynamic Analysis
- **`dg-to-kd`**: Calculate dissociation constant (Kd) from ΔG.
- **`fel`**: Calculate Free Energy Landscapes (FEL).
- **`namd-stats`**: Extract thermodynamics and kinetics from NAMD logs.
- **`harm-potential`**: Calculate harmonic spring constants for umbrella sampling.

#### Sequence & Structure Analysis
- **`contact-map`**: Calculate contact frequencies between atom selections.
- **`get-seq`**: Retrieve sequences from PDB/NCBI and run BLASTp.
- **`prody-eda`**: Perform Essential Dynamics Analysis (PCA) using ProDy.
- **`r-msa`**: Run Multiple Sequence Alignment using R's `msa` package.

#### Workflows & Automation
- **`analysis-workflow`**: Run a full suite of MD analyses across project directories.
- **`vina-screening`**: Virtual screening workflow (SMI -> PDBQT -> Vina -> Sort).
- **`virtscreen`**: Simplified Vina screening loop for existing libraries.
- **`namd-hpc-segment`**: Manage segmented NAMD simulations on HPC (SLURM).
- **`easy-htmd`**: Basic setup for high-throughput MD.

Run `mstbxanalysis [COMMAND] --help` for specific options of each tool.

## How to Add a New Analysis Script

`MSTBxAnalysis` is designed to be easily extensible. To add a new analysis tool, follow these steps:

1.  **Create a Module File:**
    Navigate to `src/mstbxanalysis/modules/` and create a new Python file. The filename should be descriptive (e.g., `sasa_analysis.py`). Note that underscores in the filename will be automatically converted to hyphens in the CLI command (e.g., `mstbxanalysis sasa-analysis`).

2.  **Define the CLI Command:**
    In your new file, import `click` and define a function named `command` decorated with `@click.command()`. This function will be the entry point for your tool.

3.  **Add Options and Arguments:**
    Use `@click.option()` to define the parameters your tool needs (input files, parameters, output names, etc.).

4.  **Implement the Logic:**
    Write your analysis code inside the `command` function or call other functions from it.

### Example Template (`src/mstbxanalysis/modules/my_new_tool.py`):
```python
import click
import MDAnalysis as mda # If needed
# Import other libraries as necessary

@click.command()
@click.option('--input', '-i', required=True, help='Path to the input file')
@click.option('--param', default=1.0, help='A numerical parameter for analysis')
@click.option('--output', '-o', default='result.dat', help='Output file path')
def command(input, param, output):
    """
    Brief description of what this tool does.
    This description will appear in the 'mstbxanalysis --help' menu.
    """
    click.echo(f"Starting analysis on {input} with parameter {param}...")

    # 1. Load data
    # 2. Perform calculations
    # 3. Save results

    click.echo(f"Analysis complete! Results saved to {output}")
```

The system will automatically detect this new file and register it as a subcommand. You can immediately run it as:
```bash
mstbxanalysis my-new-tool --input data.pdb --param 2.5
```


## Legacy Code
All original scripts from the `CompBiology-Biophysics` repository have been moved to the `old.code/` directory for reference.

## License
GPLv3
