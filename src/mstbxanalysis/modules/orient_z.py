import click
import os

@click.command()
@click.option('--pdb', required=True, help='Input PDB file.')
@click.option('--ofile', default='oriented', help='Output base name for oriented PDB (without extension).')
@click.option('--sel', default='all', help='Atom selection to orient.')
def command(pdb, ofile, sel):
    """Orient a protein along the Z-axis using VMD."""
    
    tcl_orient = f"""
package require Orient
namespace import Orient::orient

set pdb {pdb}
set ofile {ofile}
set seltext "{sel}"

mol load pdb $pdb 

proc orient_z {{ seltext }} {{ 
    # orient in z axis 
    
    set sel [atomselect top $seltext]
    set I [draw principalaxes $sel]

    set A [orient $sel [lindex $I 2] {{0 0 1}}]
    $sel move $A
    set I [draw principalaxes $sel]

    set A [orient $sel [lindex $I 2] {{0 0 1}}]
    $sel move $A
    set I [draw principalaxes $sel]
}}

# run routine
orient_z $seltext

# add chains based on segname
set all [atomselect top $seltext]
set segnames [lsort -unique [$all get segname]]
foreach seg $segnames {{
    set selseg [atomselect top "segname $seg"]
    $selseg set chain [string index $seg 3]
}}

$all writepdb $ofile.pdb
quit
"""
    tcl_file = 'orientZ-axis.tcl'
    with open(tcl_file, 'w') as f:
        f.write(tcl_orient)
    
    click.echo(f"Running VMD to orient {pdb} along Z-axis...")
    os.system(f"vmd -dispdev text -e {tcl_file}")
    
    if os.path.exists(f"{ofile}.pdb"):
        click.echo(f"Protein was Oriented to Z-axis. Output: {ofile}.pdb")
    else:
        click.echo("Error: Oriented PDB was not created. Check VMD output.")
