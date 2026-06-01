# MSTBxAnalysis

Modular analysis tools for computational biophysics and biology. This project is a refactored and modernized version of the `CompBiology-Biophysics` script collection, designed for ease of use and extensibility.

## Features
- **Modular CLI:** Use a single command `mstbxanalysis` to access all tools.
- **Easy Installation:** Install via `pip` or set up a dedicated `conda` environment.
- **Extensible Architecture:** Adding a new analysis script is as simple as dropping a Python file into the `modules/` directory.
- **Cross-Platform:** Compatible with Linux and macOS.

## Installation

### Using Conda (Recommended)
```bash
conda env create -f environment.yml
conda activate mstbxanalysis
```

### Using Pip (Recommended for Development)
```bash
pip install -e .
```
*Note: Using `-e` (editable mode) installs the package as a symbolic link to your source code. This means any changes you make to the files in `src/` will be immediately available in the `mstbxanalysis` command without needing to re-install.*

## Usage

The general syntax is:
```bash
mstbxanalysis [COMMAND] [OPTIONS]
```

### Available Commands

- **`rmsd`**: Calculate Root Mean Square Deviation (RMSD) using MDAnalysis.
- **`fel`**: Calculate Free Energy Landscapes (FEL) from two collective variables.
- **`dg-to-kd`**: Calculate dissociation constant (Kd) from Gibbs free energy (ΔG).

Run `mstbxanalysis --help` to see the full list of commands.

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
