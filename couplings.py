#!/usr/bin/env python3

'''
Analyse mode (invoked with -a) can be used here to automate the Boltzmann averaging over conformers.

Without -a, the script can be used to output csv files for NMR calculations on different molecules with different
numbers of atoms, atom labels, etc. This was useful e.g. when finding the linear scaling factors.

When calling -a, the script automatically reads in the renormalised population of each conformer. This information
is placed into the nmr input files automatically by opt2nmr.py as a comment. The ORCA .out file therefore also
contains the information, since the input file is automatically printed near the top of the .out file.
Then, it automatically averages the couplings.
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
        atom_labels = []
        atom_types = []
        couplings = []
        population = 0
        other_coupling = False
        for line in data_file:
            if "#  Population:" in line:
                population = float(line.split()[-1])
            if "NUCLEUS A" in line and "NUCLEUS B" in line:
                other_coupling = False
                if line.split()[-2] == "O":
                    other_coupling = True
                else:
                    atom_labels.append(line.split()[4] + "_" + line.split()[-1])
                    atom_types.append(line.split()[3] + "_" + line.split()[-2])
            if "Total" in line and "iso=" in line and not other_coupling:
                couplings.append(float(line.split()[-1]))
    return atom_labels, atom_types, couplings, population


if __name__ == '__main__':
    args = get_args()
    
    if args.analyse:
        file_number = 0
        for file in args.filenames:
            file_number = file_number + 1
            conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
            if file_number == 1:
                atom_labels, atom_types, couplings, population = parse_coupling_file(file)
                if atom_labels:
                    nmr_df = pd.DataFrame({
                        'atom_label': atom_labels,
                        'atom_type': atom_types,
                        'conf_{}'.format(conformer_number): couplings
                    })
                    nmr_df = nmr_df.set_index('atom_label')
                    pop = pd.Series(population, index=['conf_{}'.format(conformer_number)])
            else:
                atom_labels, atom_types, couplings, population = parse_coupling_file(file)
                if atom_labels:
                    nmr_df['conf_{}'.format(conformer_number)] = np.nan
                    for i in range(len(atom_labels)):
                        nmr_df.at[atom_labels[i], 'conf_{}'.format(conformer_number)] = couplings[i]
                    pop['conf_{}'.format(conformer_number)] = population
        pop.name = "pop"
        full_df = nmr_df.append(pop)

        # average the shieldings according to population
        full_df['avg_coupl'] = 0.0
        total_pop = 0
        for name in full_df.columns:
            if name.startswith("conf"):
                full_df['avg_coupl'] = full_df['avg_coupl'] + full_df[name]*full_df.at['pop',name]
                total_pop = total_pop + full_df.at['pop',name]
        full_df.at['pop', 'avg_coupl'] = total_pop

        # round the final value to 2 decimal places
        full_df['avg_coupl'] = full_df['avg_coupl'].round(2)

        print(full_df)

        csv_filename = "coupling_constant_data.csv"
        full_df.to_csv(csv_filename)
        print("Data written to {}.".format(csv_filename))

    else:
        for file in args.filenames:
            atom_labels, atom_types, couplings, population = parse_coupling_file(file)
            if atom_labels:
                print("FILE: {}".format(file))
                print("pop: {}".format(population))
                nmr_df = pd.DataFrame({
                    'atom_labels': atom_labels,
                    'atom_types': atom_types,
                    'coupling': couplings,
                })
                print(nmr_df)
                print()
                if args.csv:
                    csv_filename = file.replace(".out", ".csv")
                    nmr_df.to_csv(csv_filename)
                    print("Data written to {}.".format(csv_filename))