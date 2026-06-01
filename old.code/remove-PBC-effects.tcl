#! An general script to remove PBC and rot+tran effects on NAMD traj of Protein in solution
#! and Protein in membrane.  
#! 
#! @author : Ropón-Palacios G. 
#! date: May 11, 2023. 
#! change logs
#! - Fix fitAtomGroup, Tue 15 Aug, 2023. 01:08 am.
package require pbctools 

mol new files/complex_PNSC121__input121__variant5_QwikMD.psf type psf 
mol addfile reduce_1000f.dcd type dcd waitfor all 

set mem 0 
set prot 1 
set seltxtwrap "protein"
set seltxttraj  "all"

proc fitAtomGroup {mol sel } { 
	set ref [atomselect $mol $sel frame 0]
	set fitAtoms [atomselect $mol $sel]
	set nf [molinfo $mol get numframes]
	set moveAtoms [atomselect $mol all] 
	for {set frame 0} { $frame < $nf } { incr frame } {
		puts "Frame: $frame"
		$fitAtoms frame $frame
		$moveAtoms frame $frame 
		set matrix [measure fit $fitAtoms $ref]
		$moveAtoms move $matrix   		
	}
	animate write dcd traj_noPBC_fitAtomsGroup.dcd beg 0 end -1 waitfor all top
	

}


#! Remove PBC effects
#!----------------------------------------------------------------------------
if { $mem == 1} {
	pbc wrap -center com -centersel $seltxtwrap -all -compound res
	set sel [atomselect top $seltxttraj]
	animate write dcd traj_noPBC.dcd beg 0 end -1 waitfor all sel $sel
       	
} elseif { $prot == 1 } {
	pbc wrap -center com -centersel $seltxtwrap -all -compound res 
	set sel [atomselect top $seltxttraj]
	animate write dcd traj_noPBC.dcd beg 0 end -1 waitfor all sel $sel 
} else {
	puts "You haven't select any options."


}

#! Remove rot+trans 
#!------------------------------------------------------------------------------
mol delete all 
mol new files/complex_PNSC121__input121__variant5_QwikMD.psf type psf 
mol addfile traj_noPBC.dcd type dcd waitfor all 

set seltxt "protein and name CA"
fitAtomGroup top  $seltxt 

quit 




