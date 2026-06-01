import click
import importlib
import pkgutil
from . import modules

@click.group()
def cli():
    """MSTBxAnalysis: A modular tool for computational biophysics analysis."""
    pass

# Dynamically load all modules in the 'modules' subpackage
def load_modules():
    for _, module_name, _ in pkgutil.iter_modules(modules.__path__):
        full_module_name = f"mstbxanalysis.modules.{module_name}"
        module = importlib.import_module(full_module_name)
        
        # Look for a click command or group named 'command' in the module
        if hasattr(module, 'command'):
            cli.add_command(module.command, name=module_name.replace('_', '-'))

load_modules()

if __name__ == "__main__":
    cli()
