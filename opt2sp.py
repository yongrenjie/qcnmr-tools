#!/usr/bin/env python3

# Navigate to the folder in which the optimised .xyz files are in. These should be named tpss_svp_opt_<confno>.xyz
# (or something similar). Then run:
#    opt2sp.py opt_filtered_conformers.csv
# where opt_filtered_conformers.csv is the csv file containing the conformers below the energy cutoff (3 kcal/mol).
# The script then generates all required input files for the next step (single points at TPSS/def2-TZVPP), which can
# then be copied to a directory of your choice.

# Note that this script uses the file name to determine which conformers are in which .xyz file. For it to work, the
# filenames have to be of the form s3_<confno>_<other_keywords>.xyz, i.e. the number must be the second thing given.
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

    keywords = "! TPSS def2-TZVPP D3BJ CPCM(Methanol) PAL8 SP"  # Change this if desired.

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
    print()
    print("Input files will be generated for {} conformers: {}".format(len(allowed_conformers), allowed_conformers))
    print()

    ls = os.listdir()
    allowed_xyz_files = []
    for file in ls:
        if file.endswith(".xyz"):
            try:
                conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
            except:
                conformer_number = 0   # to deal with other stray .xyz files, such as crest_conformer.xyz
            if conformer_number in allowed_conformers:
                allowed_xyz_files.append(file)

    try:
        os.mkdir("s4-sp")
    except:
        pass
    print("Generating single point input files...")
    for file in allowed_xyz_files:
        conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
        inp_name = "s4-sp/s4_{}_sp_tzvpp.inp".format(conformer_number) # Change if desired

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
    print("Single point input files written to s4-sp.")
    print()
