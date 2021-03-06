#!/usr/bin/env python3

import re
import argparse
import os
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help='File containing all conformers (default crest_conformers.xyz)')
    parser.add_argument("-r", "--remove", action="store", type=int, default=0,
                        help="Number of atoms to remove from the end of each set of coordinates")
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()

    if args.filename:
        crest_file = args.filename
    else:
        if "crest_conformers.xyz" in os.listdir():
            crest_file = "crest_conformers.xyz"
        else:
            sys.exit("Please provide a valid xyz file with all conformers.")

    # determine total number of atoms
    test_file = open(crest_file, 'r')
    total_atoms = int(test_file.readline().strip())
    test_file.close()


    keywords = "! TPSS def2-SVP D3BJ CPCM(Methanol) PAL4 SP"

    try:
        os.mkdir("s2-sp")
    except:
        pass

    try:
        with open(crest_file, 'r') as crest_xyz_file:
            line_number = 0
            conformer_number = 1
            atom_number = 0
            output_file = open('s2-sp/s2_{}_sp_svp.inp'.format(conformer_number), 'w')
            comment_line = False
            for line in crest_xyz_file:
                line_number = line_number + 1
                number_of_atoms_found = re.match(r'\s*(\d+)\s+', line)
                if comment_line:
                    print("#    {}".format(line), file=output_file)
                    print("* xyz 0 1", file=output_file)
                    comment_line = False
                elif number_of_atoms_found:
                    atom_number = 0
                    if line_number > 1:
                        print("*", file=output_file)
                        output_file.close()
                        if conformer_number % 100 == 0:
                            print(conformer_number)
                        conformer_number = conformer_number + 1
                        output_file = open('s2-sp/s2_{}_sp_svp.inp'.format(conformer_number), 'w')
                    print(keywords, file=output_file)
                    print("", file=output_file)
                    comment_line = True
                else:
                    if atom_number < total_atoms - args.remove:
                        print(line.rstrip("\n"), file=output_file)
                    atom_number = atom_number + 1
            print("*", file=output_file)
            output_file.close()
            print("{} input files generated.".format(conformer_number))
            print()
    except:
        print("Please provide a valid xyz file with all conformers.")
        print()
