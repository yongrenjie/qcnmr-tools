# qcnmr-tools
Assorted scripts (Python 3) to aid with calculation of NMR properties.

**qcrest**

Automatically takes an .xyz file (in Angstroms), converts it to a `coord` file (in Bohrs), prints a submission script for crest, and submits the job using the newly generated `coord` file.
Requires that the directory with crest is added to `$PATH`.
