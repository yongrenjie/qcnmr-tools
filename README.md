# qcnmr-tools

**This README is not fully up-to-date!**

Assorted scripts (Python 3) to aid with calculation of NMR properties.

The NMR calculation workflow is adapted from [Grimme *et al.*, *Angew. Chem. Int. Ed.* **2017,** *56* (46), 14763–14769](https://doi.org/10.1002/anie.201708266). Below the key steps (as well as where the scripts come in) are described in more detail.

1. Generate a conformer-rotamer ensemble using CREST.

 - `qcrest` is useful here. It takes an .xyz file (in Angstroms), automatically converts it to a `coord` file (in Bohrs), prints a submission script for CREST, and submits the job to the cluster using the newly generated `coord` file. In order for this to work, the directory containing CREST must be added to `$PATH`.
 - The defaults for qcrest are to request 4 cores, use methanol as solvent (GBSA), and to use an energy cutoff of 6 kcal/mol. These can be changed using command line arguments; use `qcrest -h` for more information.
 - The output of the CREST job is saved to `<name>_crest.out` (where `<name>.xyz` was the original file submitted with `qcrest`). This file will contain the GFN-xTB energies. The full conformer ensemble (without rotamers) is in `crest_conformers.xyz` and at this stage can be visualised using e.g. Avogadro. If desired, the conformer-rotamer ensemble can be found in `crest_rotamers_6.xyz`.

2. The CRE is then subjected to a single-point calculation with a relatively cheap level of theory (Grimme uses PBEh-3c, I used TPSS/def2-SVP/D3BJ/CPCM(Methanol)).

 - In theory, this can be done using the allxyz feature in ORCA. However, I dislike this for several reasons, and have opted to generate one input file per conformer. These reasons are given below in decreasing order of severity: 
   - Sometimes the `.out` file gets truncated/corrupted for no apparent reason;
   - With large allxyz files the program can crash due to (what appears to be memory issues);
   - If there is a problem with just one structure then the entire job will be terminated;
   - Running *n* conformers in one job can take longer than is necessary, compared to running one conformer per job in *n* jobs;
   - Avoids having to use `-ca` with `qorca41`.
 - By running `crestxyz_to_sp.py` on the `crest_conformers.xyz` file, one input file per conformer will be automatically generated. Right now the program is hard-coded to put in certain keywords; this can obviously be changed if needed.

3. Conformers above a certain energy threshold are then rejected.

 - The script `extract_energies.py` will help greatly with this step. It is capable of parsing any of the following:
   - multiple single-point `.out` files (by running `extract_energies.py *.out`), such as those generated in the previous step;
   - the CREST output file `<name>_crest.out`;
   - ORCA output files from SP or Opt jobs on allxyz files.
 - With the flag `-c` it prints a list of all conformers to a csv file.
 - With the flag `-t X`, it will automatically output a csv file containing a list of conformers below X kcal/mol (relative to the lowest-energy conformer). Grimme uses X = 3, I use X = 4.
 - At this stage, to produce some graphics similar to those found in Grimme's SI, the script `line_plot_energies.py` is capable of reading in multiple csv files. It will then plot the energies of each conformer at different levels of theory (one csv file per level of theory). This is useful for checking whether CREST is indeed finding all or most of the low-energy conformers. However, I find that this is not a particularly useful way of presenting data.
 - Instead I have chosen to use a scatter plot to present the data. The file `scatter_energies.py` takes two csv files, one earlier and one after: for example, this can be the csv files (generated for all conformers) from the CREST job and the first SP job, for example. The question we really want to answer is: given that we will be using the energies from the "later" step to filter the CRE, *is the "earlier" step finding all the conformers which would pass this later filter*? By using the `-t` option, the script automatically colours the points which would *pass* the next filter in green. Then it becomes much clearer to see how well the "earlier" step is doing at finding these conformers which would pass the next filter.

4. The filtered conformers are subjected to DFT optimisation at a cheap level of theory (here again TPSS/def2-SVP/D3BJ/CPCM(Methanol)).

 - As before, `extract_energies.py` will plot/display the energies as desired.
 - Again, `filter_allxyz.py` (in combination with the csv file which `extract_energies.py` provides) will produce the filtered allxyz file so that an ORCA job can be run using it.

5. In Grimme's paper the authors filter the conformer ensemble again, based on the energies of the optimised structures.

6. For all remaining conformers, a single-point calculation at a higher level of theory is used (here likely TPSS/def2-TZVPP/D3BJ/CPCM(Methanol), although I plan to test a few things and see if it makes any difference).

7. The conformer ensemble is filtered again based on a final energy threshold from the previous step.

 - All in all there are four filters: (1) GFN-xTB energy of < 6 kcal/mol (step 1 in this README); (2) cheap DFT energy of < 3 kcal/mol (step 3); (3) cheap DFT optimised energy of < x kcal/mol (step 5); (4) expensive DFT (or other method) energy of < y kcal/mol (step 7).

8. NMR shieldings and couplings are calculated in ORCA and subjected to Boltzmann averaging (using electronic energy or Gibbs free energy?).

 - `anmr_shieldings.py` currently has some functionality to parse the chemical shifts of carbon atoms from the shielding job, but it needs to be mostly rewritten.
 - Also, it may be interesting to compare simply scaling the shifts to TMS versus doing linear scaling according to the method of Pierens ([*J. Comput. Chem.* **2014,** *35* (18), 1388–1394](https://doi.org/10.1002/jcc.23638)).

9. In Grimme's paper they then solve the spin Hamiltonian, but this is only really necessary in order to produce sensible spectra. Since we are only really interested in the shifts and couplings, this step is unnecessary.
