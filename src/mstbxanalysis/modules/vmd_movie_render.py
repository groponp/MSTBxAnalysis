import click
import subprocess
import os

@click.command()
@click.option('--vmd_scene', required=True, help='VMD scene file (.vmd or .tcl)')
@click.option('--ofile', default='movie.mp4', help='Output movie file name (default: movie.mp4)')
@click.option('--width', default=700, help='Movie width (default: 700)')
@click.option('--height', default=700, help='Movie height (default: 700)')
@click.option('--fps', default=25, help='Output movie FPS (default: 25)')
def command(vmd_scene, ofile, width, height, fps):
    """Render a movie from a VMD scene using Tachyon and FFmpeg."""
    
    movie_dir = "movie_frames"
    tcl_script = f"""
source {vmd_scene}
display resize {width} {height}
exec mkdir -p {movie_dir}

set nf [molinfo top get numframes]

for {{set i 0}} {{ $i < $nf }} {{incr i}} {{
	animate goto $i 
    display update on 
	puts "Rendering Frame #: $i"
	render TachyonInternal {movie_dir}/frame$i.ppm 
}}

exit 
"""
    
    script_name = "tmp_movie_render.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD to render frames...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
        
        click.echo(f"Encoding movie with ffmpeg...")
        ffmpeg_cmd = [
            "ffmpeg", "-y", "-pattern_type", "glob", "-r", str(fps), 
            "-i", f"{movie_dir}/*.ppm", "-vcodec", "libx264", "-crf", "25", 
            "-pix_fmt", "yuv420p", "-vf", f"fps={fps},scale={width}:{height}", ofile
        ]
        subprocess.run(ffmpeg_cmd, check=True)
        
    except FileNotFoundError as e:
        click.echo(f"Error: {e}. Please ensure VMD and FFmpeg are installed and in your PATH.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error during rendering or encoding: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
        # Optional: cleanup frames
        # if os.path.exists(movie_dir):
        #     import shutil
        #     shutil.rmtree(movie_dir)
    
    click.echo(f"Movie rendering finished! Output: {ofile}")
