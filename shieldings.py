#!/usr/bin/env python3

'''
Analyse mode (invoked with -a) can be used here to automate the Boltzmann averaging over conformers.

Without -a, the script can be used to output csv files for NMR calculations on different molecules with different
numbers of atoms, atom labels, etc. This was useful e.g. when finding the linear scaling factors.

When calling -a, the script automatically reads in the renormalised population of each conformer. This information
is placed into the nmr input files automatically by opt_to_nmr.py as a comment. The ORCA .out file therefore also
contains the information, since the input file is automatically printed near the top of the .out file.
Then, it automatically averages the shifts and scales them according to the slope/intercept previously found.
'''


import argparse
import re
import pandas as pd

SLOPE_1H_PBE0_ccPVTZ = -1.072135032
INTERCEPT_1H_PBE0_ccPVTZ = 31.29178358
SLOPE_13C_PBE0_ccPVTZ = -1.044992801
INTERCEPT_13C_PBE0_ccPVTZ = 186.6631559
# chemical shift = (shielding - intercept)/slope


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        action='store',
                        help='.out files to read.',
                        nargs="*")
    parser.add_argument("-c", "--csv", action="store_true", help="Output a csv file for every nmr output file found")
    parser.add_argument("-a", "--analyse", action="store_true", help="Enter analyse mode (see comments in script for details")
    return parser.parse_args()


def parse_shielding_file(file):
    with open(file, 'r') as data_file:
        shielding_block = False
        atom_labels = []
        atom_types = []
        shieldings = []
        population = 0
        for line in data_file:
            if "#  Population:" in line:
                population = float(line.split()[-1])
            if "CHEMICAL SHIELDING SUMMARY" in line:
                shielding_block = True
            elif "Timings for individual modules" in line:
                shielding_block = False
            if re.match(r'\s+\d+\s+[C|H]\s+', line) and shielding_block:
                atom_labels.append(line.split()[0])
                atom_types.append(line.split()[1])
                shieldings.append(line.split()[2])
    return atom_labels, atom_types, shieldings, population


if __name__ == '__main__':
    args = get_args()

    if args.analyse:
        file_number = 0
        for file in args.filenames:
            file_number = file_number + 1
            conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
            if file_number == 1:
                atom_labels, atom_types, shieldings, population = parse_shielding_file(file)
                if atom_labels:
                    nmr_df = pd.DataFrame({
                        'atom_labels': atom_labels,
                        'atom_types': atom_types,
                        'conf_{}'.format(conformer_number): shieldings
                    })
                    pop = pd.Series(population, index=['conf_{}'.format(conformer_number)])
            else:
                atom_labels, atom_types, shieldings, population = parse_shielding_file(file)
                if atom_labels:
                    nmr_df['conf_{}'.format(conformer_number)] = shieldings
                    pop['conf_{}'.format(conformer_number)] = population
        pop.name = "pop"
        full_df = nmr_df.append(pop)

        # TODO average the populations; all the data is inside the df...

        print(full_df)

    else:
        for file in args.filenames:
            atom_labels, atom_types, shieldings, population = parse_shielding_file(file)
            if atom_labels:
                print("FILE: {}".format(file))
                nmr_df = pd.DataFrame({
                    'atom_labels': atom_labels,
                    'atom_types': atom_types,
                    'shieldings': shieldings
                })
                print(nmr_df)
                print()
                if args.csv:
                    csv_filename = file.replace(".out", ".csv")
                    nmr_df.to_csv(csv_filename, columns=['atom_labels', 'atom_types', 'shieldings'])
                    print("Data written to {}.".format(csv_filename))
