# MSTBxAnalysis - AI Instructions

This repository has been refactored from `CompBiology-Biophysics` into a modular Python package named `MSTBxAnalysis`.

## Project Versioning & Maintenance

- **Current Version:** `0.5.0-beta`
- **Versioning Policy:** Increments follow a `.20` cycle (e.g., from `0.5.0-beta` to `0.5.20-beta` before jumping to `0.6.0-beta`).
- **Tool Ingestion (`addtool/`):** The directory `addtool/` (git-ignored) is used as a staging area for new scripts. Check this folder for legacy code that needs porting to the modular CLI.

## Current Tools Index

### Core MDAnalysis
- `rmsd`, `mda-rgyr`, `mda-rmsf`, `mda-2dmatrix`, `mda-convert-traj`, `pbc-fix`.

### VMD/Tcl
- `vmd-sasa`, `vmd-get-box`, `vmd-pbc-wrap`, `vmd-rmsd-residue`, `vmd-segid-to-chain`, `vmd-merge-pdb`, `vmd-reduce-traj`, `vmd-movie-render`, `vmd-molpack`, `vmd-molywood`, `vmd-make-segname`, `vmd-jarzynski`, `vmd-make-tclforces`, `orient-z`, `remove-rot-trans`.

### Prep & Building
- `bigbabel`, `charmm-gui-prepare`, `co-mol-md`, `gmx-atom-index`, `make-flooding`, `namd-to-charmm`, `namd-to-gmx`, `sdf-to-pdb`.

### Stat & Thermo
- `dg-to-kd`, `fel`, `namd-stats`, `harm-potential`.

### Seq & Struct
- `contact-map`, `get-seq`, `prody-eda`, `r-msa`.

### Workflows
- `analysis-workflow`, `vina-screening`, `virtscreen`, `namd-hpc-segment`, `easy-htmd`.

## Development Rules

- **Adding Commands:** 
  - To add a new analysis, create a file in `src/mstbxanalysis/modules/`.
  - The filename (with underscores converted to hyphens) will become the subcommand name.
  - The file MUST contain a `@click.command()` decorated function named `command`.
- **Dependencies:** Use the `environment.yml` or `pyproject.toml` to manage dependencies. Key scientific libraries include `MDAnalysis`, `NumPy`, `Pandas`, `Matplotlib`, and `Seaborn`.
- **Legacy Reference:** Original scripts are available in `old.code/`. Use these as references when porting functionality to the new modular system.

## Sub-Agents & Skills
- Use the `codebase_investigator` for understanding how complex modules are ported.
- Use `managing-python-dependencies` for any changes to `pyproject.toml` or `environment.yml`.

## File Structure
- `src/mstbxanalysis/`: Core package.
- `src/mstbxanalysis/main.py`: CLI Entry point.
- `src/mstbxanalysis/modules/`: Subcommand implementations.
- `old.code/`: Legacy scripts.
- `environment.yml`: Conda environment definition.
- `pyproject.toml`: Build system and package metadata.
