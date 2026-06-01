import click
import subprocess
import os

@click.command()
@click.option('--pdb', required=True, help='Input PDB file (step1_pdbreader.pdb)')
@click.option('--fix_sel', default='protein and name CA', help='Atoms to fix during orientation (SMD)')
@click.option('--pull_sel', default='protein and name CA', help='Atoms to pull during orientation (SMD)')
@click.option('--md_type', type=click.Choice(['MD', 'SMD']), default='MD', help='Type of MD setup (MD or SMD)')
@click.option('--toppar_dir', default='../../toppar', help='Directory containing topology files')
@click.option('--box_pad', default=10, help='Box padding in Angstroms')
@click.option('--ion_conc', default=0.150, help='Ionic concentration in mol/L')
@click.option('--ofile', default='system_build', help='Base name for output files')
def command(pdb, fix_sel, pull_sel, md_type, toppar_dir, box_pad, ion_conc, ofile):
    """Build a complete biomolecule system (orient, topology, solvate, ionize) using VMD."""
    
    tcl_script = f"""
package require psfgen
package require solvate
package require autoionize

proc orientMol {{molID typeMD pullatoms fixatoms ofile}} {{
    if {{$typeMD == "MD"}} {{
    	set selall [atomselect $molID all]
    	set center [measure center $selall]
    	set move_dist [transoffset [vecsub {{0 0 0}} $center]]
    	$selall move $move_dist 
    	$selall writepdb $ofile
    }} elseif {{$typeMD == "SMD"}} {{
        set selall [atomselect $molID all]
        set selanchor [atomselect $molID "$fixatoms"] 
        set selpulling [atomselect $molID "$pullatoms"]
        set anchor [measure center $selanchor]
        set pulling [measure center $selpulling]
        set axis [vecsub $pulling $anchor]
        set M [transvecinv $axis] 
        $selall move $M 
        set M [transaxis y -90] 
        $selall move $M 
        $selall writepdb $ofile
    }}
}}

set molID [mol new {pdb} type pdb waitfor all]
orientMol $molID {md_type} "{pull_sel}" "{fix_sel}" "{ofile}_orient.pdb"

topology {toppar_dir}/top_all36_prot.rtf
topology {toppar_dir}/top_all36_na.rtf
topology {toppar_dir}/toppar_water_ions.str
topology {toppar_dir}/top_all36_lipid.rtf
topology {toppar_dir}/top_all36_carb.rtf 
topology {toppar_dir}/stream/carb/toppar_all36_carb_glycopeptide.str 

mol new {ofile}_orient.pdb type pdb waitfor all
set sel [atomselect top "protein"]
set segnames [lsort -unique [$sel get segname]]
foreach segname $segnames {{
    pdbalias atom ILE CD1 CD
    set seg $segname
    set sel [atomselect top "protein and segname $segname"]
    $sel writepdb tmp.pdb 
    segment $seg {{pdb tmp.pdb}}
    coordpdb tmp.pdb $seg 
    guesscoord
}}

set sel [atomselect top "hetero and not protein"]
if {{ [$sel num] > 0 }} {{
    set segnames [lsort -unique [$sel get segname]]
    foreach segname $segnames {{
        pdbalias residue ANE ANE5AC
        pdbalias residue BGL BGLCNA
        pdbalias residue AMA AMAN   
        pdbalias residue BMA BMAN 
        pdbalias residue BGA BGAL 
        pdbalias residue AFU AFUC
        pdbalias residue AGA AGALNA
        set seg $segname
        set sel [atomselect top "hetero and not protein and segname $segname"]
        $sel writepdb tmp.pdb
        segment $seg {{pdb tmp.pdb}}
        coordpdb tmp.pdb $seg 
        guesscoord
    }}
}}

regenerate angles dihedrals 
writepsf {ofile}.psf
writepdb {ofile}.pdb
mol delete all 

proc cytoplasm {{psf pdb boxpad ionconc typeMD ofile}} {{
    set molID [mol new $psf type psf waitfor all]
    mol addfile $pdb type pdb waitfor all
    set sel [atomselect $molID "all"]
    set minmax [measure minmax $sel]
    $sel delete
    set xsp [lindex [lindex $minmax 0] 0]
    set ysp [lindex [lindex $minmax 0] 1]
    set zsp [lindex [lindex $minmax 0] 2]
    set xep [lindex [lindex $minmax 1] 0]
    set yep [lindex [lindex $minmax 1] 1]
    set zep [lindex [lindex $minmax 1] 2]
    
    set xp [expr abs($xep - $xsp)]
    set yp [expr abs($yep - $ysp)]
    set zp [expr abs($zep - $zsp)]

    set dp [expr sqrt($xp*$xp+$yp*$yp+$zp*$zp)]
    set box_length [expr $dp + 2*$boxpad]
    
    set xsb  [expr $xsp - ($box_length-$xp)/2]
    set ysb  [expr $ysp - ($box_length-$yp)/2]
    set zsb  [expr $zsp - ($box_length-$zp)/2]
    set xeb  [expr $xep + ($box_length-$xp)/2]
    set yeb  [expr $yep + ($box_length-$yp)/2]
    set zeb  [expr $zep + ($box_length-$zp)/2]

    set boxmin [list $xsb $ysb $zsb]
    set boxmax [list $xeb $yeb $zeb]

    solvate $psf $pdb -minmax [list $boxmin $boxmax] -o ${{ofile}}_solvated
    autoionize -psf ${{ofile}}_solvated.psf -pdb ${{ofile}}_solvated.pdb -cation SOD -anion CLA -sc $ionconc -o ${{ofile}}_final
    mol delete $molID
}}

cytoplasm {ofile}.psf {ofile}.pdb {box_pad} {ion_conc} {md_type} {ofile}
quit
"""
    
    script_name = "tmp_molpack.tcl"
    with open(script_name, "w") as f:
        f.write(tcl_script)
    
    click.echo(f"Running VMD MolPack building process...")
    try:
        subprocess.run(["vmd", "-dispdev", "text", "-e", script_name], check=True)
    except FileNotFoundError:
        click.echo("Error: 'vmd' command not found. Please ensure VMD is installed.")
    except subprocess.CalledProcessError as e:
        click.echo(f"Error running VMD MolPack: {e}")
    finally:
        if os.path.exists(script_name):
            os.remove(script_name)
        if os.path.exists("tmp.pdb"):
            os.remove("tmp.pdb")
    
    click.echo(f"MolPack building finished! Final output: {ofile}_final.psf/pdb")
