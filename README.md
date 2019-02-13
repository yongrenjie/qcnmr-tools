# qcnmr-tools
Assorted scripts (Python 3) to aid with calculation of NMR properties.


**sp-energies**

Takes as input an .out file from an ORCA single point calculation on an .allxyz file. The script then does two things:
1. Plots the energy of each input structure in kcal/mol relative to the lowest energy structure.
2. Prints a list of conformers below a certain threshold energy.

**qcrest**

Automatically takes an .xyz file (in Angstroms), converts it to a `coord` file (in Bohrs), prints a submission script for crest, and submits the job using the newly generated `coord` file.
Requires that the directory with crest is added to `$PATH`.
