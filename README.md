# README.md

A collection of Python 3 scripts to process ORCA output files. There are several steps:

 1. Conformer generation (CREST or GROMACS).
 2. Cheap single-point energies to weed out low-population conformers.
 3. Geometry optimisation.
 4. (More accurate) single-point energies to get Boltzmann populations.
 5. NMR chemical shift calculations.
 6. NMR coupling constant calculations.

Many of these scripts could probably be cut to short bash one-liners. For example, to parse one NMR calculation output,

    sed -n '/CHEMICAL SHIELDING/,/Timings/p' | awk -v OFS=, 'NF==4 && $2 ~ /^[HC]$/ {print $1, $2, $3}' | sort -t, -k2,2 -k1n
 
works very well... the scaling can be done with some arithmetic in `awk`... and multiple files could be handled with `join`.
