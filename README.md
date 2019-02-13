# qcnmr-tools
Assorted scripts (Python 3) to aid with calculation of NMR properties.

Use the optional argument `-h` to find out more about what these can do!

**allxyz_to_inp**

Converts an .allxyz file into multiple ORCA .inp files. Keywords are hardcoded.

**allxyz_to_xyz**

Converts an .allxyz file into individual .xyz files for each structure, as well as one large .xyz file containing all structures.

Avogadro chokes on the .allxyz file format but opens the large .xyz file just fine (to scroll through the structures, use Extensions > Animation).

**extract-energies**

Extracts and manipulates energies from (either) a CREST output file, or an ORCA single point calculation on an .allxyz file. Use `-h` with this, it has several useful functions.

**plot_conformer_energies**

Reads energies from csv files produced by the previous two scripts (use those with `-c` to generate the csv files) and plots them on a graph.

**qcrest**

Automatically takes an .xyz file (in Angstroms), converts it to a `coord` file (in Bohrs), prints a submission script for crest, and submits the job using the newly generated `coord` file.

Requires that the directory with crest is added to `$PATH`.
