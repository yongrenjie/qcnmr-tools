#!/usr/bin/env python3

import matplotlib.pyplot as plt
import pandas as pd
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        action='store',
                        help='.csv file(s) to plot energies from. '
                             'For scatter mode, first filename = before filter, second filename = after filter.',
                        nargs="*")
    parser.add_argument("-s",
                        "--scatter",
                        action="store_true",
                        help="Puts lowest energy conformer at 0 kcal/mol for all graphs for a scatter plot.")
    parser.add_argument("-l",
                        "--line",
                        action="store_true",
                        help="Puts first conformer at 0 kcal/mol for all graphs, "
                             "analogous to figures in Grimme's SI (default).")
    return parser.parse_args()

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

def get_short_list(file):
    conformer_energies = []
    with open(file, 'r') as csv_file:
        for line in csv_file:
            if not line.lstrip().startswith(","):
                conformer_energies.append(float(line.rstrip("\n").split(",")[-1]))
    return conformer_energies

if __name__ == '__main__':
    args = get_args()
    file_number = 1
    full_df = pd.DataFrame()
    for filename in args.filenames:
        base_name = filename.rstrip(".csv")
        if file_number == 1:
            num, ene = get_full_list(filename)
            full_df.loc[:, 'num'] = num
            full_df.loc[:, base_name] = ene
        else:
            ene = get_short_list(filename)
            full_df.loc[:, base_name] = ene
        file_number = file_number + 1

    column_names = list(full_df.columns)

    if args.line:
        for column in full_df[column_names[1:]]:
            full_df[column] = full_df[column] - full_df[column][0]
        print(full_df)
        column_names = list(full_df.columns)
        full_df.plot(x=0, y=column_names[1:], linewidth=0.75)
        plt.show()
    elif args.scatter:
        for column in full_df[column_names[1:]]:
            full_df[column] = full_df[column] - full_df[column].min()
        print(full_df)
        column_names = list(full_df.columns)
        full_df.plot(x=1, y=2, kind="scatter", s=4)
        plt.show()