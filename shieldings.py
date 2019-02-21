#!/usr/bin/env python3

import argparse
import re
import pandas as pd

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        action='store',
                        help='.xyz files to convert into input files.',
                        nargs="*")
    parser.add_argument("-c", "--csv", action="store_true", help="Output a csv file for every nmr output file found")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()

    for file in args.filenames:
        with open(file, 'r') as data_file:
            shielding_block = False
            atom_labels = []
            atom_types = []
            shieldings = []
            for line in data_file:
                if "CHEMICAL SHIELDING SUMMARY" in line:
                    shielding_block = True
                elif "Timings for individual modules" in line:
                    shielding_block = False
                if re.match(r'\s+\d+\s+[C|H]\s+', line) and shielding_block:
                    atom_labels.append(line.split()[0])
                    atom_types.append(line.split()[1])
                    shieldings.append(line.split()[2])
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
