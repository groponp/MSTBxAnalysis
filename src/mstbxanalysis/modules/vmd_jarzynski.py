import click
import os

@click.command()
@click.option('--ofile', default='jarzynski.tcl', help='Output TclForces script name (default: jarzynski.tcl)')
@click.option('--target_pdb', default='marks.pdb', help='PDB with marks for pulling/fixing')
@click.option('--k', default=5.0, help='Force constant kcal/mol/A^2 (default: 5.0)')
@click.option('--v', default=0.00002, help='Pulling velocity A/timestep (default: 0.00002)')
@click.option('--out_data', default='force_pulling.dat', help='Output data file (default: force_pulling.dat)')
def command(ofile, target_pdb, k, v, out_data):
    """Generate a NAMD TclForces script for Jarzynski equality pulling."""
    
    tcl_content = f"""
# TclForces script for Jarzynski equality 
set targetAtomPdb {target_pdb}
set mark1 1.0 
set mark2 2.0

set ligtargets   {{}}
set ligmasses    {{}}
set helixtargets {{}}
set helixmasses  {{}}

set inStream [open $targetAtomPdb r] 
foreach line [split [read $inStream] \\n] {{
	set type [string trim [string range $line 0 5]]
	set name [string trim [string range $line 12 15]] 
	set resid [string trim [string range $line 22 25]]
	set beta [string trim [string range $line 60 65]]
	set occupancy [string trim [string range $line 54 59]]
	set segname [string trim [string range $line 72 75]] 
	
	if {{ ($type eq "ATOM" || $type eq "HETATM") && $beta == $mark1 }} {{ 
		lappend ligtargets "$segname $resid $name" 
		lappend ligmasses  $occupancy 
	}} elseif {{ ($type eq "ATOM" || $type eq "HETATM") && $beta == $mark2 }} {{ 
		lappend helixtargets "$segname $resid $name" 
		lappend helixmasses  $occupancy 
	}}
}} 
close $inStream 

set ligatoms   {{}}
foreach target1 $ligtargets {{ 
	lassign $target1 segname resid atom 
	set atomindex [atomid $segname $resid $atom] 
	lappend ligatoms $atomindex 
	addatom $atomindex 
}} 

set helixatoms {{}} 
foreach target2 $helixtargets {{ 
	lassign $target2 segname resid atom 
	set atomindex [atomid $segname $resid $atom] 
	lappend helixatoms $atomindex 
	addatom $atomindex 
}} 

set ligand [addgroup $ligatoms] 
set helix  [addgroup $helixatoms] 

set Tclfreq 50 
set t 0 

set c1x	0.0
set c1y 0.0 
set c1z 0.0 

set c2x 0.0
set c2y 0.0 
set c2z 0.0

set k {k} 
set v {v} 

set outfilename {out_data} 

proc calcforces {{}} {{ 
	global Tclfreq t k v ligand helix c1x c1y c1z c2x c2y c2z outfilename 
	
	loadcoords coordinate 
	
	set r1 $coordinate($helix) 
	set r1x [lindex $r1 0] 
	set r1y [lindex $r1 1] 
	set r1z [lindex $r1 2] 

	set r2 $coordinate($ligand) 
	set r2x [lindex $r2 0] 
	set r2y [lindex $r2 1] 
	set r2z [lindex $r2 2] 
	
	set f1x [ expr $k*($c1x-$r1x)] 
	set f1y [ expr $k*($c1y-$r1y)] 
	set f1z [ expr $k*($c1z-$r1z)]
	set f1 [list $f1x $f1y $f1z]

	set f2z [ expr $k*($v*$t-($r2z-$c2z))] 
	set f2 [list 0.0 0.0 $f2z] 

	addforce $helix  $f1 
	addforce $ligand $f2
	
	if {{ [expr $t % $Tclfreq] == 0}} {{
		set outfile [open $outfilename a] 
		set time [expr $t*2/1000.0] 
		set dt 0.002 
		set Workz [expr ($f2z*$v*$dt)/69.479] 
		puts $outfile "$time\\t$r2z\\t$f2z\\t$Workz"
		close $outfile 
	}} 
	incr t 
}}
"""
    
    with open(ofile, "w") as f:
        f.write(tcl_content)
    
    click.echo(f"NAMD TclForces script generated: {ofile}")
    click.echo("Note: This script is intended to be used with NAMD, not VMD.")
