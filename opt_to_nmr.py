#!/usr/bin/env python3

# Navigate to the folder in which the optimised .xyz files are in. These should be named tpss_svp_opt_<confno>.xyz
# (or something similar). Then run:
#    opt_to_nmr.py nmr_filtered_conformers.csv
# where nmr_filtered_conformers.csv is the csv file containing conformers for NMR calculations.
# The script then generates all required input files for the shielding calculations, which can then be copied to a
# directory of your choice.

# Note that this script uses the file name to determine which conformers are in which .xyz file. For it to work, the
# filenames have to be of the form s3_<confno>_<other_keywords>.xyz, i.e. the number must be the second thing given.
# The previous scripts should automatically do this.

import os
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("csvname", action='store', help='csv file to filter conformers by.')
    parser.add_argument("-n", "--nuclei", type=int, nargs="*", help="Labels of H nuclei to calculate J(CH) for.")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    csv_file = args.csvname

    keywords = "! PBE0 cc-pVTZ cc-pVTZ/JK D3BJ CPCM(Methanol) PAL4"  # Change this if desired.
    eprnmr_shielding = "%eprnmr\n" \
                        "    Ori = GIAO\n" \
                        "    Nuclei = all C { shift }\n" \
                        "    Nuclei = all H { shift }\n" \
                        "end"
    eprnmr_coupling_hh =  "%eprnmr\n" \
                        "    Ori = GIAO\n" \
                        "    Nuclei = all H { ssfc, ist = 1 }\n" \
                        "    SpinSpinRThresh 6.0\n" \
                        "end"
    hydrogen_atoms = ""
    if args.nuclei:
        for i in args.nuclei:
            hydrogen_atoms = hydrogen_atoms + str(i) + " "
    else:
        hydrogen_atoms = "all H "
    eprnmr_coupling_ch = "%eprnmr\n" \
                         "    Ori = GIAO\n" \
                         "    Nuclei = " + hydrogen_atoms + "{ ssall, ist = 1 }\n" \
                         "    SpinSpinRThresh 1.3\n" \
                         "end"

    # reads in allowed conformers, energies, and (renormalised) populations from the csv file
    allowed_conformers = []
    allowed_conformer_energies = []
    allowed_conformer_populations = []
    with open(csv_file, 'r') as filter_file:
        line_number = 0
        for line in filter_file:
            line_number = line_number + 1
            if line_number > 1:
                allowed_conformers.append(int(line.split(",")[1]))
                allowed_conformer_energies.append(float(line.split(",")[2]))
                allowed_conformer_populations.append(float(line.split(",")[6]))
    print(allowed_conformers)

    ls = os.listdir()
    allowed_xyz_files = []
    for file in ls:
        if file.endswith(".xyz") and not file.startswith("."):
            # second conditional is necessary, otherwise it tries to read all the hidden files
            conformer_number = int(file.split(".")[-2].split("_")[-1])  # gets conformer number from file name
            if conformer_number in allowed_conformers:
                allowed_xyz_files.append(file)

    for file in allowed_xyz_files:
        conformer_number = int(file.split(".")[-2].split("_")[-1])  # gets conformer number from file name
        inp_name = "s6_{}_nmr_shielding.inp".format(conformer_number) # Change if desired

        with open(file, 'r') as xyz_file:
            line_count = 1
            with open(inp_name, 'w') as inp_file:
                print(keywords, file=inp_file)
                print("", file=inp_file)
                print("#  S4-SP: {}".format(allowed_conformer_energies[allowed_conformers.index(conformer_number)]),
                      file=inp_file)  # prints def2-TZVPP energy as a comment
                print("#  Population: {}".format(allowed_conformer_populations[allowed_conformers.index(conformer_number)]),
                      file=inp_file)
                print("", file=inp_file)
                print("*xyz 0 1", file=inp_file)
                for line in xyz_file:
                    if line_count >= 3:
                        print(line.rstrip("\n"), file=inp_file)
                    line_count = line_count + 1
                print("*", file=inp_file)
                print("", file=inp_file)
                print(eprnmr_shielding, file=inp_file)