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
import pandas as pd
import numpy as np


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        action='store',
                        help='.out files to read.',
                        nargs="*")
    parser.add_argument("-c", "--csv", action="store_true", help="Output a csv file for every nmr output file found")
    parser.add_argument("-a", "--analyse", action="store_true", help="Enter analyse mode (see comments in script for details")
    return parser.parse_args()


def parse_coupling_file(file):
    with open(file, 'r') as data_file:
        atom_1_labels = []
        atom_2_labels = []
        atom_1_types = []
        atom_2_types = []
        couplings = []
        population = 0
        for line in data_file:
            if "#  Population:" in line:
                population = float(line.split()[-1])
            if "NUCLEUS A" in line and "NUCLEUS B" in line:
                print(line)
                atom_1_labels.append(line.split()[4])
                atom_1_types.append(line.split()[3])
                atom_2_labels.append(line.split()[-1])
                atom_2_types.append(line.split()[-2])
            if "Total" in line and "iso=" in line:
                couplings.append(float(line.split()[-1]))

    return atom_1_labels, atom_1_types, atom_2_labels, atom_2_types, couplings, population


if __name__ == '__main__':
    args = get_args()
    '''
    if args.analyse:
        file_number = 0
        for file in args.filenames:
            file_number = file_number + 1
            conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
            if file_number == 1:
                atom_labels, atom_types, shieldings, population = parse_shielding_file(file)
                if atom_labels:
                    nmr_df = pd.DataFrame({
                        'atom_label': atom_labels,
                        'atom_type': atom_types,
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

        # average the shieldings according to population
        full_df['avg_shield'] = 0.0
        total_pop = 0
        for name in full_df.columns:
            if name.startswith("conf"):
                full_df['avg_shield'] = full_df['avg_shield'] + full_df[name]*full_df.at['pop',name]
                total_pop = total_pop + full_df.at['pop',name]
        full_df.at['pop', 'avg_shield'] = total_pop

        # scale the shieldings to obtain chemical shifts
        full_df['shift'] = 0.0
        for i in full_df.index:
            if isinstance(i, int):
                if full_df.at[i, 'atom_type'] == "C":
                    full_df.at[i, 'shift'] = (full_df.at[i, 'avg_shield'] - INTERCEPT_13C_PBE0_ccPVTZ)/SLOPE_13C_PBE0_ccPVTZ
                elif full_df.at[i, 'atom_type'] == "H":
                    full_df.at[i, 'shift'] = (full_df.at[i, 'avg_shield'] - INTERCEPT_1H_PBE0_ccPVTZ)/SLOPE_1H_PBE0_ccPVTZ
        full_df.at['pop','shift'] = np.nan
        print(full_df)

        csv_filename = "chemical_shift_data.csv"
        full_df.to_csv(csv_filename)
        print("Data written to {}.".format(csv_filename))
    '''
    if 1:
    # else:
        for file in args.filenames:
            atom_1_labels, atom_1_types, atom_2_labels, atom_2_types, couplings, population = parse_coupling_file(file)
            if atom_1_labels:
                print("FILE: {}".format(file))
                print("pop: {}".format(population))
                nmr_df = pd.DataFrame({
                    'atom_1_label': atom_1_labels,
                    'atom_1_type': atom_1_types,
                    'atom_2_label': atom_2_labels,
                    'atom_2_type': atom_2_types,
                    'coupling': couplings,
                })
                print(nmr_df)
                print()
                if args.csv:
                    csv_filename = file.replace(".out", ".csv")
                    nmr_df.to_csv(csv_filename)
                    print("Data written to {}.".format(csv_filename))