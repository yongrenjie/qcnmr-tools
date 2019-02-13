# qcnmr-tools
Assorted scripts (Python 3) to aid with calculation of NMR properties.

**allxyz_to_inp**

Converts an .allxyz file into multiple ORCA .inp files. Keywords are hardcoded.

**allxyz_to_xyz**

Converts an .allxyz file into individual .xyz files for each structure, as well as one large .xyz file containing all structures.

Avogadro chokes on the .allxyz file format but opens the large .xyz file just fine (to scroll through the structures, use Extensions > Animation).

**sp-energies**

Takes as input an .out file from an ORCA single point calculation on an .allxyz file. The script then does two things:
1. Plots the energy of each input structure in kcal/mol relative to the lowest energy structure.
2. Prints a list of conformers below a certain threshold energy.

**qcrest**

Automatically takes an .xyz file (in Angstroms), converts it to a `coord` file (in Bohrs), prints a submission script for crest, and submits the job using the newly generated `coord` file.
Requires that the directory with crest is added to `$PATH`.
