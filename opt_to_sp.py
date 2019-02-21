#!/usr/bin/env python3

# Navigate to the folder in which the optimised .xyz files are in. These should be named tpss_svp_opt_<confno>.xyz
# (or something similar). Then run:
#    opt_to_sp.py opt_filtered_conformers.csv
# where opt_filtered_conformers.csv is the csv file containing the conformers below the energy cutoff (3 kcal/mol).
# The script then generates all required input files for the next step (single points at TPSS/def2-TZVPP), which can
# then be copied to a directory of your choice.

# Note that this script uses the file name to determine which conformers are in which .xyz file. For it to work, the
# filenames have to be of the form <...>_<confno>.xyz, i.e. there must be an underscore before the number.
# The previous scripts should automatically do this.

import os
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("csvname", action='store', help='csv file to filter conformers by')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    csv_file = args.csvname

    keywords = "! TPSS def2-TZVPP D3BJ CPCM(Methanol) PAL4 SP"  # Change this if desired.

    # reads in allowed conformers and their energies from the csv file
    allowed_conformers = []
    allowed_conformer_energies = []
    with open(csv_file, 'r') as filter_file:
        line_number = 0
        for line in filter_file:
            line_number = line_number + 1
            if line_number > 1:
                allowed_conformers.append(int(line.split(",")[1]))
                allowed_conformer_energies.append(float(line.split(",")[2]))
    print(allowed_conformers)

    ls = os.listdir()
    allowed_xyz_files = []
    for file in ls:
        if file.endswith(".xyz"):
            conformer_number = int(file.split(".")[-2].split("_")[-1])  # gets conformer number from file name
            if conformer_number in allowed_conformers:
                allowed_xyz_files.append(file)

    for file in allowed_xyz_files:
        conformer_number = int(file.split(".")[-2].split("_")[-1])  # gets conformer number from file name
        inp_name = file.replace(".xyz", ".inp").replace("svp", "tzvpp").replace("opt", "sp") # Change if desired

        with open(file, 'r') as xyz_file:
            line_count = 1
            with open(inp_name, 'w') as inp_file:
                print(keywords, file=inp_file)
                print("", file=inp_file)
                print("#  S3-Opt: {}".format(allowed_conformer_energies[allowed_conformers.index(conformer_number)]),
                      file=inp_file)  # prints def2-SVP energy as a comment
                print("", file=inp_file)
                print("*xyz 0 1", file=inp_file)
                for line in xyz_file:
                    if line_count >= 3:
                        print(line.rstrip("\n"), file=inp_file)
                    line_count = line_count + 1
                print("*", file=inp_file)
                print("", file=inp_file)