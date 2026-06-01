import click
import subprocess
import os

@click.command()
@click.option('--fasta', required=True, help='Input FASTA file.')
@click.option('--method', default='ClustalW', help='MSA method (ClustalW, ClustalOmega, Muscle).')
@click.option('--output-pdf', default='seqAln.pdf', help='Output PDF filename.')
def command(fasta, method, output_pdf):
    """
    Run Multiple Sequence Alignment using R 'msa' package.
    Requires R and 'msa' package installed.
    """
    if not os.path.exists(fasta):
        click.echo(f"Error: Fasta file {fasta} not found.")
        return

    r_script_content = f"""
library("msa")

# Ensure texshade.sty is available
texshade_path <- system.file("tex", "texshade.sty", package="msa")
if (file.exists(texshade_path)) {{
  file.copy(texshade_path, ".", overwrite = TRUE)
}}

seqFile <- readAAStringSet("{fasta}")
seqAln <- msa(seqFile, method="{method}", verbose=TRUE)
print(seqAln)

msaPrettyPrint(seqAln, output="tex", showNames="left", showLogo="top",
               askForOverwrite=FALSE, shadingColors="black",
               consensusColors="HotCold", logoColors="rasmol", 
               shadingMode="similar")

# Compile tex to pdf
# Note: texi2pdf might not be in all R installations, or might require tools::
tools::texi2pdf("seqAln.tex", clean=TRUE)
"""

    with open("run_msa.R", "w") as f:
        f.write(r_script_content)

    click.echo("Running Rscript for MSA...")
    try:
        subprocess.run(["Rscript", "run_msa.R"], check=True)
        if os.path.exists("seqAln.pdf") and output_pdf != "seqAln.pdf":
            os.rename("seqAln.pdf", output_pdf)
        click.echo(f"MSA finished. Output saved to {output_pdf}")
    except subprocess.CalledProcessError:
        click.echo("Error running Rscript. Ensure R and 'msa' package are installed.")
    finally:
        # Cleanup
        if os.path.exists("run_msa.R"):
            os.remove("run_msa.R")
        if os.path.exists("seqAln.tex"):
            os.remove("seqAln.tex")
        if os.path.exists("texshade.sty"):
            os.remove("texshade.sty")

if __name__ == '__main__':
    command()
