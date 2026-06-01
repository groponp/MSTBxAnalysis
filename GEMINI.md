# MSTBxAnalysis - AI Instructions

This repository has been refactored from `CompBiology-Biophysics` into a modular Python package named `MSTBxAnalysis`.

## Core Architecture

- **CLI Tool:** `mstbxanalysis` (installed via `pip` or `conda`).
- **Modular System:** All analysis subcommands are located in `src/mstbxanalysis/modules/`.
- **Dynamic Loading:** The CLI dynamically loads any Python file in the `modules/` directory that contains a `click` command named `command`.

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
