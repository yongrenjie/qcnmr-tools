#!/usr/bin/env python3

'''
Analyse mode (invoked with -a) can be used here to automate the Boltzmann averaging over conformers.

Without -a, the script can be used to output csv files for NMR calculations on different molecules with different
numbers of atoms, atom labels, etc. This was useful e.g. when finding the linear scaling factors.

When calling -a, the script automatically reads in the renormalised population of each conformer. This information
is placed into the nmr input files automatically by opt2nmr.py as a comment. The ORCA .out file therefore also
contains the information, since the input file is automatically printed near the top of the .out file.
Then, it automatically averages the shifts and scales them according to the slope/intercept previously found.

Often there are nuclei which are rendered equivalent by symmetry or by rapid interconversion (e.g. the three protons in
a methyl group). If these have the labels 13, 14, and 15, then pass these labels (separated by commas) with -e:
    shieldings.py *.out -a -e 13,14,15
The script will automatically average these shifts and place the mean in a new row.
Multiple groups of nuclei can be specified, e.g.
    shieldings.py *.out -a -e 13,14,15 16,17,18 20,21
Note that the use of -e <NUCLEI> only has an effect when in analyse mode.
'''


import argparse
import re
import pandas as pd
import numpy as np

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
    parser.add_argument("-e", "--equiv", type=str, nargs="*", help="Put in symmetry-related nuclei here, separated by commas")
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
                shieldings.append(float(line.split()[2]))
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
        full_df.at['pop', 'shift'] = np.nan

        # average symmetry-equivalent nuclei
        if args.equiv:
            for nuclei_set in args.equiv:
                nuclei = nuclei_set.split(",")
                shifts_to_be_averaged = []
                for i in full_df.index:
                    if full_df.at[i, 'atom_label'] in nuclei:
                        shifts_to_be_averaged.append(full_df.at[i, 'shift'])
                average = sum(shifts_to_be_averaged)/len(shifts_to_be_averaged)
                average_shift = pd.Series(average, index=['shift'])
                average_shift.name = nuclei_set
                full_df = full_df.append(average_shift)

        # round final chemical shift to 2 decimal places
        full_df['shift'] = full_df['shift'].round(2)
        print(full_df)

        csv_filename = "chemical_shift_data.csv"
        full_df.to_csv(csv_filename)
        print("Data written to {}.".format(csv_filename))

    else:
        for file in args.filenames:
            atom_labels, atom_types, shieldings, population = parse_shielding_file(file)
            if atom_labels:
                print("FILE: {}".format(file))
                nmr_df = pd.DataFrame({
                    'atom_label': atom_labels,
                    'atom_type': atom_types,
                    'shielding': shieldings
                })
                print(nmr_df)
                print()
                if args.csv:
                    csv_filename = file.replace(".out", ".csv")
                    nmr_df.to_csv(csv_filename)
                    print("Data written to {}.".format(csv_filename))
