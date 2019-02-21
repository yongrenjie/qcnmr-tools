# qcnmr-tools

**This README is not fully up-to-date!**

Assorted scripts (Python 3) to aid with calculation of NMR properties.

The NMR calculation workflow is adapted from [Grimme *et al.*, *Angew. Chem. Int. Ed.* **2017,** *56* (46), 14763–14769](https://doi.org/10.1002/anie.201708266). Below the key steps (as well as where the scripts come in) are described in more detail. Each individual script has more explanation.

The directory containing the scripts must be added to `$PATH`, and the files must be made executable by running `chmod u+x *` in the directory containing the scripts.

Please use a separate folder for each of the following steps! Not only is it much cleaner, but also required for some of the scripts to work properly.

**Step 1: Generate a conformer-rotamer ensemble using CREST**
 - Construct an xyz file using software of your choice (in Angstroms).
 - Run `qcrest <file_name>.xyz`; this takes an .xyz file (in Angstroms), automatically converts it to a `coord` file (in Bohrs), prints a submission script for CREST, and submits the job to the cluster using the newly generated `coord` file.
 - The defaults for qcrest are to request 4 cores, use methanol as solvent (GBSA), and to use an energy cutoff of 6 kcal/mol. These can be changed using command line arguments; use `qcrest -h` for more information.
 - The output of the CREST job is saved to `<name>_crest.out` (where `<name>.xyz` was the original file submitted with `qcrest`). This file will contain the GFN-xTB energies. The full conformer ensemble (without rotamers) is in `crest_conformers.xyz` and at this stage can be visualised using e.g. Avogadro. If desired, the conformer-rotamer ensemble can be found in `crest_rotamers_6.xyz`.

**Step 2: The CRE is then subjected to a single-point calculation with a relatively cheap level of theory. Any conformers above a certain energy (relative to the lowest energy conformer) are rejected.** (default TPSS/def2-SVP/D3BJ/CPCM(Methanol), cutoff 4 kcal/mol)

 - Run `crestxyz_to_sp.py` on the `crest_conformers.xyz` file. This will generate one input file per conformer. The ORCA keywords are hard-coded; this can obviously be changed if needed.
 - In theory, this can be done using the allxyz feature in ORCA. The `old_scripts` folder contains several scripts that help with generating and manipulating allxyz files. However, I dislike this for several reasons. In decreasing order of severity, these are: 
   - Sometimes the `.out` file gets truncated/corrupted for no apparent reason;
   - With large allxyz files the program can crash due to (what appears to be memory issues);
   - If there is a problem with just one structure then the entire job will be terminated;
   - Running *n* conformers in one job can take longer than is necessary, compared to running one conformer per job in *n* jobs;
   - Avoids having to use `-ca` with `qorca41`
 - Once the calculations are done, run `extract_energies.py *.out` to get a table of all energies (in kcal/mol relative to the lowest energy conformer). This can be output to a csv file by using the option `-c`.
 - To restrict the output to those conformers within X kcal/mol, use the option `-t X`, which also automatically prints the results to a csv file (`sp_filtered_conformers.csv`). This csv file can be used for the next step.

**Step 3: Optimise all conformers which pass the previous filter. Any conformers above a certain energy (relative to the lowest energy conformer) are rejected.** (default TPSS/def2-SVP/D3BJ/CPCM(Methanol))

 - In order to generate the input files for the optimisation, both `crest_conformers.xyz` (generated in Step 1 as output of the CREST program) as well as `sp_filtered_conformers.csv` (generated in Step 2) are required.
 - Run `crestxyz_to_opt.py crest_conformers.xyz sp_filtered_conformers.csv`. This generates one input file for each conformer that is in the csv file.
 - Once the calculations are done, `extract_energies.py *.out` can again be used to generate the csv file `opt_filtered_conformers.csv` which contains all conformers below X kcal/mol.

**Step 4: Calculate the energy of all conformers at a higher level of theory.** (default TPSS/def2-TZVPP/D3BJ/CPCM(Methanol))
 - Copy all the optimised xyz files, as well as `opt_filtered_conformers.csv`, to another directory!
 - In this directory, run `opt_to_sp.py opt_filtered_conformers.csv`. This generates input files for every conformer found in the csv file.

**Step 5: The conformer ensemble is filtered again; anything below 4% population is rejected.**
 - `extract_energies.py` will be able to extract the energies, but does not (yet) have the capability to calculate populations.

**Tools for data analysis**

 - To produce graphics analogous to that found in Grimme's SI, run `line_plot_energies.py <csv1>.csv <csv>2.csv ...`. Make sure that all the csv files passed to this script have the same number of conformers. This script plot the energies of each conformer at different levels of theory (one csv file per level of theory). The zero of energy is taken to be the first conformer. However, I find that this is not a particularly useful way of presenting data.
 - Instead I have chosen to use a scatter plot to present the data. The file `scatter_energies.py` takes two csv files, one earlier and one after: for example, this can be the csv files (generated for all conformers) from the CREST job and the first SP job, for example. The question we really want to answer is: given that we will be using the energies from the "later" step to filter the CRE, *is the "earlier" step finding all the conformers which would pass this later filter*? By using the `-t X` option, the script automatically colours the points which would *pass* the next filter of X kcal/mol in green. Then it becomes much clearer to see how well the "earlier" step is doing at finding these conformers which would pass the next filter.