#!/usr/bin/env python3

import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        action='store',
                        help='.xyz files to convert into input files.',
                        nargs="*")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()

    keywords = input("Please enter the desired keywords:")

    for file in args.filenames:
        conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name

        inp_name = "s3-opt/s3_{}_svp_opt.inp".format(conformer_number)

        with open(file, 'r') as xyz_file:
            line_count = 1
            with open(inp_name, 'w') as inp_file:
                print(keywords, file=inp_file)
                print("", file=inp_file)
                print("*xyz 0 1", file=inp_file)
                for line in xyz_file:
                    if line_count >= 3:
                        print(line.rstrip("\n"), file=inp_file)
                    line_count = line_count + 1
                print("*", file=inp_file)
                print("", file=inp_file)
