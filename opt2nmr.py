#!/usr/bin/env python3

# Navigate to the folder in which the optimised .xyz files are in. These should be named s3_<no>_opt_svp.xyz
# (or something similar). Then run:
#    opt2nmr.py nmr_filtered_conformers.csv
# where nmr_filtered_conformers.csv is the csv file containing conformers for NMR calculations.
# The script then generates all required input files for the shielding and coupling calculations in
# separate directories.

# Note that this script uses the file name to determine which conformers are in which .xyz file. For it to work, the
# filenames have to be of the form s3_<confno>_<other_keywords>.xyz, i.e. the number must be the second thing given.
# The previous scripts should automatically do this.

import os
import argparse
import sys

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("csvname", action='store', help='csv file to filter conformers by.')
    parser.add_argument("-n", "--nuclei", type=int, nargs="*", help="Labels of H nuclei to calculate J(HH)/J(CH) for. "
                                                                    "WARNING: USE ATOM LABELS STARTING FROM 1, i.e. "
                                                                    "exactly what is shown in Avogadro")
    parser.add_argument("-a", "--atoms", action="store", type=int,
                        help="Number of atoms to keep in input file (count this from 1)")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    csv_file = args.csvname

    # Check if nuclei for couplings are not specified
    if args.nuclei:
        print()
        print("Couplings will be calculated for the following H nuclei: {}".format(args.nuclei))
    else:
        print()
        print("WARNING: Couplings will be calculated for all H nuclei!")
        print("Please consider specifying a subset of nuclei to calculate couplings for "
              "in order to reduce computational time.")
        print()
        confirmation = input("If you want to go ahead with this, please type 'yes'.\n"
                             "Otherwise, please enter the labels of the nuclei to calculate J(HH)/J(CH) for "
                             "(separated by commas). Note that these nuclei should be counted starting from 1, not 0: ")
        if confirmation.lower() == "yes":
            pass
        else:
            try:
                args.nuclei = []
                for i in confirmation.split(","):
                    args.nuclei.append(int(i.strip()))
                print("Couplings will be calculated for the following H nuclei: {}".format(args.nuclei))
            except:
                sys.exit("Non-integer input detected! Exiting...")
    print()

    # generate keywords and eprnmr block for ORCA input file
    shielding_keywords = "! PBE0 cc-pVTZ cc-pVTZ/JK D3BJ CPCM(Methanol) PAL8 \n\n%maxcore 4000"  # Change this if desired.
    coupling_keywords = "! PBE0 pcJ-2 AutoAux D3BJ CPCM(Methanol) PAL8 \n\n%maxcore 4000"  # Change this if desired.
    eprnmr_shielding = "%eprnmr\n" \
                        "    Ori = GIAO\n" \
                        "    Nuclei = all C { shift }\n" \
                        "    Nuclei = all H { shift }\n" \
                        "end"
    eprnmr_coupling_hh = "%eprnmr\n"
    eprnmr_coupling_ch = "%eprnmr\n"
    if args.nuclei:
        for i in args.nuclei:
            eprnmr_coupling_hh = eprnmr_coupling_hh + "    Nuclei = " + str(i) + " { ssfc, ist = 1 }\n"
            eprnmr_coupling_ch = eprnmr_coupling_ch + "    Nuclei = " + str(i) + " { ssall, ist = 1 }\n"
    else:
        eprnmr_coupling_hh = eprnmr_coupling_hh + "    Nuclei = all H { ssfc, ist = 1 }\n"
        eprnmr_coupling_ch = eprnmr_coupling_ch + "    Nuclei = all H { ssall, ist = 1 }\n"

    eprnmr_coupling_hh = eprnmr_coupling_hh + "    SpinSpinRThresh 3.6\nend"
    eprnmr_coupling_ch = eprnmr_coupling_ch + "    SpinSpinRThresh 1.3\nend"


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
    print()
    print("Input files will be generated for {} conformers: {}".format(len(allowed_conformers), allowed_conformers))
    print()

    ls = os.listdir()
    allowed_xyz_files = []
    for file in ls:
        if file.endswith(".xyz") and not file.startswith("."):
            # second conditional is necessary, otherwise it tries to read all the hidden files
            try:
                conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
            except:
                conformer_number = 0  # in case of stray xyz files
            if conformer_number in allowed_conformers:
                allowed_xyz_files.append(file)


    # generate shielding input files
    try:
        os.mkdir("s5-shielding")
    except:
        pass
    print("Generating shielding input files...")
    for file in allowed_xyz_files:
        conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
        inp_name = "s5-shielding/s5_{}_nmr_shielding.inp".format(conformer_number) # Change if desired

        with open(file, 'r') as xyz_file:
            atom_number = 0
            line_count = 1
            with open(inp_name, 'w') as inp_file:
                print(shielding_keywords, file=inp_file)
                print("", file=inp_file)
                print("#  S4-SP: {}".format(allowed_conformer_energies[allowed_conformers.index(conformer_number)]),
                      file=inp_file)  # prints def2-TZVPP energy as a comment
                print("#  Population: {}".format(allowed_conformer_populations[allowed_conformers.index(conformer_number)]),
                      file=inp_file)
                print("", file=inp_file)
                print("*xyz 0 1", file=inp_file)
                for line in xyz_file:
                    if line_count >= 3:
                        if args.atoms and atom_number < args.atoms:
                            print(line.rstrip("\n"), file=inp_file)
                        elif not args.atoms:
                            print(line.rstrip("\n"), file=inp_file)
                        else:
                            pass
                        atom_number = atom_number + 1
                    line_count = line_count + 1
                print("*", file=inp_file)
                print("", file=inp_file)
                print(eprnmr_shielding, file=inp_file)
    print("Shielding input files written to s5-shielding.")
    print()

    # generate coupling input files
    try:
        os.mkdir("s6-coupling")
    except:
        pass
    print("Generating coupling input files...")
    for file in allowed_xyz_files:
        conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
        inp_name = "s6-coupling/s6_{}_nmr_coupling.inp".format(conformer_number)  # Change if desired

        with open(file, 'r') as xyz_file:
            atom_number = 0
            line_count = 1
            with open(inp_name, 'w') as inp_file:
                print(coupling_keywords, file=inp_file)
                print("", file=inp_file)
                print("#  S4-SP: {}".format(allowed_conformer_energies[allowed_conformers.index(conformer_number)]),
                      file=inp_file)  # prints def2-TZVPP energy as a comment
                print("#  Population: {}".format(
                    allowed_conformer_populations[allowed_conformers.index(conformer_number)]),
                      file=inp_file)
                print("", file=inp_file)
                print("*xyz 0 1", file=inp_file)
                for line in xyz_file:
                    if line_count >= 3:
                        if args.atoms and atom_number < args.atoms:
                            print(line.rstrip("\n"), file=inp_file)
                        elif not args.atoms:
                            print(line.rstrip("\n"), file=inp_file)
                        else:
                            pass
                        atom_number = atom_number + 1
                    line_count = line_count + 1
                print("*", file=inp_file)
                print("", file=inp_file)
                print(eprnmr_coupling_hh, file=inp_file)
    print("Coupling input files written to s6-coupling.")
    print()

    print()