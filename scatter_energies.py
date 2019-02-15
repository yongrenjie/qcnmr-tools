#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("earlier_csv",
                        action='store',
                        help='.csv file from an earlier step (before filtering). ')
    parser.add_argument("later_csv",
                        action='store',
                        help='.csv file from a later step (after filtering). ')
    parser.add_argument('-t',
                        '--threshold',
                        type=int,
                        action='store',
                        help='Energy cutoff (in kcal/mol) for the next round of filtering. '
                             'For more explanation see the comments in the source code.')
    return parser.parse_args()

'''
def get_full_list(file):
    conformer_count = 1
    conformer_numbers = []
    conformer_energies = []
    with open(file, 'r') as csv_file:
        for line in csv_file:
            if not line.lstrip().startswith(","):
                conformer_numbers.append(conformer_count)
                conformer_count = conformer_count + 1
                conformer_energies.append(float(line.rstrip("\n").split(",")[-1]))
    return conformer_numbers, conformer_energies
'''

def get_energies(file):
    conformer_energies = []
    with open(file, 'r') as csv_file:
        for line in csv_file:
            if not line.lstrip().startswith(","):
                conformer_energies.append(float(line.rstrip("\n").split(",")[-1]))
    return conformer_energies

if __name__ == '__main__':
    args = get_args()
    full_df = pd.DataFrame()

    earlier_energies = np.array(get_energies(args.earlier_csv))
    later_energies = np.array(get_energies(args.later_csv))

    earlier_energies = earlier_energies - np.amin(earlier_energies)
    later_energies = later_energies - np.amin(later_energies)

    fig, ax = plt.subplots()
    ax.plot(earlier_energies, later_energies)

    for column in full_df[column_names[1:]]:
        full_df[column] = full_df[column] - full_df[column].min()
        print(full_df)
        column_names = list(full_df.columns)
        full_df.plot(x=1, y=2, kind="scatter", s=4)
        plt.show()