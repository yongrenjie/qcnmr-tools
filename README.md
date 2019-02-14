# qcnmr-tools
Assorted scripts (Python 3) to aid with calculation of NMR properties.

The NMR calculation workflow is adapted from [Grimme *et al.*, *Angew. Chem. Int. Ed.* **2017,** *56* (46), 14763–14769](https://doi.org/10.1002/anie.201708266). Below the key steps (as well as where the scripts come in) are described in more detail.

1. Generate a conformer-rotamer ensemble using CREST.

 - `qcrest` is useful here. It takes an .xyz file (in Angstroms), automatically converts it to a `coord` file (in Bohrs), prints a submission script for CREST, and submits the job to the cluster using the newly generated `coord` file. In order for this to work, the directory containing CREST must be added to `$PATH`.
 - The default energy threshold in CREST is 6 kcal/mol, i.e. it does not return any conformers above this threshold. This can be set manually by changing the code in `qcrest`. Right now this cannot be set from the command line using `qcrest`. However, solvent (GBSA) as well as the number of threads can be set from the command line. Use `qcrest -h` for more information.
 - The output of the CREST job is saved to `<name>_crest.output` (where `<name>.xyz` was the original file submitted with `qcrest`). This file will contain the GFN-xTB energies. The full conformer ensemble (without rotamers) is in `crest_conformers.xyz` and at this stage can be visualised using e.g. Avogadro. If desired, the conformer-rotamer ensemble can be found in `crest_rotamers_6.xyz`.

2. The CRE is then subjected to a single-point calculation with a relatively cheap level of theory (Grimme uses PBEh-3c, I used TPSS/def2-SVP/D3BJ/CPCM(Methanol)).

 - This can be easily done in ORCA by using `*xyzfile <charge> <mult> crest_conformers.allxyz`. The allxyz file format is detailed in the ORCA manual.
 - However, ORCA will not accept the `crest_conformers.xyz` file which CREST output in the previous step. In order to overcome this, the script `crestxyz_to_allxyz.py` will convert the .xyz file into an .allxyz file ready for use with ORCA.

3. Conformers above a certain energy threshold are then rejected.

 - The script `extract_energies.py` will help greatly with this step. By using the command line argument `-t X`, it will automatically output a csv file containing a list of conformers below X kcal/mol (relative to the lowest-energy conformer). Grimme uses X = 3.
 - This csv file can then be read by `filter_allxyz.py` which extracts only the desired conformers from `crest_conformers.allxyz` and places them in a new allxyz file.
 - At this stage, to produce some graphics similar to those found in Grimme's SI, the script `plot_energies_from_csv.py` is capable of reading in multiple csv files. It will then plot the energies of each conformer at different levels of theory (one csv file per level of theory). This is useful for checking whether CREST is indeed finding all or most of the low-energy conformers. There is still some work to be done in terms of making the plot prettier, but for now it is functional.

4. The filtered conformers are subjected to DFT optimisation at a cheap level of theory (here again TPSS/def2-SVP/D3BJ/CPCM(Methanol)).

 - As described previously, `filter_allxyz.py` will produce the filtered allxyz file so that an ORCA job can be run using it.

5. In Grimme's paper the authors filter the conformer ensemble again, based on the energies of the optimised structures.

6. For all remaining conformers, a single-point calculation at a higher level of theory is used (here likely TPSS/def2-TZVPP/D3BJ/CPCM(Methanol), although I plan to test a few things and see if it makes any difference).

7. The conformer ensemble is filtered again based on a final energy threshold from the previous step.

  - All in all there are four filters: (1) GFN-xTB energy of < 6 kcal/mol (step 1 in this README); (2) cheap DFT energy of < 3 kcal/mol (step 3); (3) cheap DFT optimised energy of < x kcal/mol (step 5); (4) expensive DFT (or other method) energy of < y kcal/mol (step 7).

8. NMR shieldings and couplings are calculated in ORCA and subjected to Boltzmann averaging (using electronic energy or Gibbs free energy?).

 - `anmr_shieldings.py` currently has some functionality to parse the chemical shifts of carbon atoms from the shielding job, but it needs to be mostly rewritten.
 - Also, it may be interesting to compare simply scaling the shifts to TMS versus doing linear scaling according to the method of Pierens ([*J. Comput. Chem.* **2014,** *35* (18), 1388–1394](https://doi.org/10.1002/jcc.23638)).

9. In Grimme's paper they then solve the spin Hamiltonian, but this is only really necessary in order to produce sensible spectra. Since we are only really interested in the shifts and couplings, this step is unnecessary.
