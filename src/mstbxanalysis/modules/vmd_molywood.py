import click
import subprocess
import os

@click.command()
@click.option('--vmd_scene', required=True, help='VMD scene file for Molywood')
@click.option('--name', default='movieHD', help='Output movie name (default: movieHD)')
@click.option('--res', default='600,600', help='Resolution (default: 600,600)')
@click.option('--fps', default=15, help='FPS (default: 15)')
def command(vmd_scene, name, res, fps):
    """Generate a Molywood script and execute Molywood for movie creation."""
    
    moly_content = f"""$ global fps={fps} render=t draft=f name={name} restart=t
$ scene0 visualization={vmd_scene} resolution={res} ambient_occlusion=t

# scene0
do_nothing         t=1s
rotate             axis=z angle=180 t=4s sigmoid=sls  
zoom_in            scale=1.2

highlight  selection='protein' style=surf color=red t=2s
{{rotate  axis=y angle=720 t=2s sigmoid=sls fraction=:0.25; zoom_in scale=1.5}}
rotate  axis=y angle=720 t=2s sigmoid=sls fraction=0.25:0.5

highlight  selection='chain A' style=surf color=red t=2s mode=u 
rotate  axis=y angle=720 t=2s sigmoid=sls fraction=0.5:0.75
{{rotate  axis=y angle=720 t=2s sigmoid=sls fraction=0.75:; zoom_out scale=1.5}}
"""
    
    moly_file = "script.moly"
    with open(moly_file, "w") as f:
        f.write(moly_content)
    
    click.echo(f"Running Molywood with generated script...")
    try:
        subprocess.run(["molywood", "-i", moly_file], check=True)
    except FileNotFoundError:
        click.echo("Error: 'molywood' command not found. Please ensure Molywood is installed.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running Molywood: {e}")
    finally:
        # if os.path.exists(moly_file):
        #     os.remove(moly_file)
        pass
    
    click.echo(f"Molywood processing finished!")
