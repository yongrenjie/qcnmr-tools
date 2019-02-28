# qcnmr-tools

Assorted scripts (Python 3) to aid with calculation of NMR properties.

The NMR calculation workflow is adapted from [Grimme *et al.*, *Angew. Chem. Int. Ed.* **2017,** *56* (46), 14763–14769](https://doi.org/10.1002/anie.201708266). The conformer generation uses a newer MTD/GC methodology from Grimme ([ChemRxiv](https://chemrxiv.org/articles/Exploration_of_Chemical_Compound_Conformer_and_Reaction_Space_with_Meta-Dynamics_Simulations_Based_on_Tight-Binding_Quantum_Chemical_Calculations/7660532)), which was shown to be superior to the MF/MD/GC methodology in the *Angew* paper. Below, the key steps (as well as where the scripts come in) are described in more detail. Each individual script has more explanation.

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
 - Once the calculations are done, run `energies.py *.out` to get a table of all energies (in kcal/mol relative to the lowest energy conformer). This can be output to a csv file by using the option `-c`.
 - To restrict the output to those conformers within X kcal/mol, use the option `-t X`, which also automatically prints the results to a csv file (`sp_filtered_conformers.csv`). This csv file can be used for the next step.

**Step 3: Optimise all conformers which pass the previous filter. Any conformers above a certain energy (relative to the lowest energy conformer) are rejected.** (default TPSS/def2-SVP/D3BJ/CPCM(Methanol))

 - In order to generate the input files for the optimisation, both `crest_conformers.xyz` (generated in Step 1 as output of the CREST program) as well as `sp_filtered_conformers.csv` (generated in Step 2) are required.
 - Run `crestxyz_to_opt.py crest_conformers.xyz sp_filtered_conformers.csv`. This generates a folder, `s3-opt`, which contains all the input files for the optimisation. By default, the input files include the `NumFreq` keyword which requests numerical frequencies; this can be turned off by using `--nofreq`.
 - Once the calculations are done, `energies.py *.out` can again be used to generate the csv file `opt_filtered_conformers.csv` which contains all conformers below X kcal/mol.

**Step 4: Calculate the energy of all conformers at a higher level of theory and select only the conformers which contribute a cumulative X% population** (default TPSS/def2-TZVPP/D3BJ/CPCM(Methanol))
 - Copy all the optimised xyz files, as well as `opt_filtered_conformers.csv`, to another directory!
 - In this directory, run `opt_to_sp.py opt_filtered_conformers.csv`. This generates input files for every conformer found in the csv file.
 - After the calculations are done, `energies.py` will be again able to extract the energies. Using the flag `-p X`, the script will automatically calculate Boltzmann weights as well as populations. It then chooses the conformers which contribute a total of X% cumulative population, renormalises the populations of the remaining conformers, and produces `nmr_filtered_conformers.csv`. **This script assumes no degeneracy in the conformers! Be careful with systems possessing any kind of symmetry!**

**Step 5: Calculate NMR parameters for all surviving conformers**

 - To generate the input files for the NMR calculations, copy `nmr_filtered_conformers.csv` to the folder containing the optimised `.xyz` files.
 - Run `opt_to_nmr.py nmr_filtered_conformers.csv -n <NUCLEI>`. Multiple atom labels may be specified after `-n`; it serves to specify which hydrogen atoms the one-bond C–H coupling constants will be calculated for. **NOTE: Because of some quirks of ORCA input, the atom labels given here should be counted from 1, as opposed to the usual 0.**
 - Three folders will be generated:
   - `s5-shieldings`, with input files for calculation of NMR shifts
   - `s6a-HHcouplings`, with input files for H–H couplings. These jobs only calculate the Fermi contact contribution to the coupling constant. In the case of H–H couplings, this has been shown to be the main contributor; however, I have not done any systematic analysis or scaling to experimental values... yet.
    - `s6b-CHcouplings`, with input files for one-bond C–H couplings. These calculate all contributions to the coupling constant, not just the Fermi contact term. Note that these take a long time to run, ca. 1 hour per coupling constant on four cores!

**Step 6: Obtain Boltzmann-averaged chemical shifts and coupling constants**

 - For chemical shifts: navigate to the folder containing the shielding .out files, then run `shieldings.py *.out -a`. This generates a fairly self-explanatory csv file which contains shieldings for all conformers, populations, etc. The chemical shifts are calculated by linear scaling of the isotropic shielding. The slopes and intercepts (for 1H and 13C) are hard-coded; they can be changed if desired.
 - `shieldings.py` is capable of averaging shifts of multiple equivalent nuclei using `-e`. See the comments at the top of the script for more details.
 - Likewise, for couplings, `couplings.py *.out -a` will do the job, but does not have the same `-e` functionality.
 
**Tools for data analysis**

 - To produce graphics analogous to that found in Grimme's SI, run `line_plot_energies.py <csv1>.csv <csv>2.csv ...`. Make sure that all the csv files passed to this script have the same number of conformers. This script plot the energies of each conformer at different levels of theory (one csv file per level of theory). The zero of energy is taken to be the first conformer. However, I find that this is not a particularly useful way of presenting data.
 - Instead I have chosen to use a scatter plot to present the data. The file `scatter_energies.py` takes two csv files, one earlier and one after: for example, this can be the csv files (generated for all conformers) from the CREST job and the first SP job, for example. The question we really want to answer is: given that we will be using the energies from the "later" step to filter the CRE, *is the "earlier" step finding all the conformers which would pass this later filter*? By using the `-t X` option, the script automatically colours the points which would *pass* the next filter of X kcal/mol in green. Then it becomes much clearer to see how well the "earlier" step is doing at finding these conformers which would pass the next filter.
 
 **Miscellaneous things**
 
  - `ls *.inp -l | wc -l` counts how many input files are in a folder.
  - `grep -o "ORCA TERMINATED NORMALLY" *.out | wc -l` counts how many jobs are done.