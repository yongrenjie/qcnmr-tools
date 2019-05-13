#!/usr/bin/env python3

import re
import argparse
import os
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", default="crest_conformers.xyz",
                        help='File containing all conformers (default crest_conformers.xyz).')
    parser.add_argument("-a", "--atoms", action="store", type=int,
                        help="Number of atoms at the beginning of each set of coordinates to keep"
                             "(everything else will be removed).")
    parser.add_argument("-r", "--remove", action="store", type=int, default=0,
                        help="Number of atoms to remove from the end of each set of coordinates.")
    return parser.parse_args()


def is_positive_integer(str):
    # checks if a string is an integer
    # warning: don't feed this floats; int("1.2") throws ValueError but int(1.9) returns 1
    try:
        a = int(str)
    except:
        return False
    # checks if str is positive
    if a > 0:
        return True
    else:
        return False


if __name__ == '__main__':
    args = get_args()

    # gets file name and makes sure it exists
    crest_file = args.filename
    if not os.path.isfile(crest_file):
        sys.exit("Please provide a valid xyz file with all conformers.\n"
                 "Use 'crest2sp.py -h' for help.")

    # determine number of atoms to keep
    if args.atoms:
        atoms_to_keep = args.atoms
    else:
        with open(crest_file, "r") as test_file:
            atoms_to_keep = int(test_file.readline().strip())

    # set ORCA keyword line depending on user input
    default_keyword_line = "! TPSS def2-SVP D3BJ CPCM(Methanol) SP PAL8"
    keyword_line = input("The default keyword line is: {} \n"
                         "Please enter the desired keyword line, "
                         "or leave blank to use the default keywords: ".format(default_keyword_line))
    if keyword_line.strip() == "":
        keyword_line = default_keyword_line

    # make the directory, if it doesn't exist
    try:
        os.mkdir("s2-sp")
    except:
        pass

    # generate the ORCA SP input files
    with open(crest_file, 'r') as crest_xyz_file:
        # initialise variables
        line_number = 0
        conformer_number = 0
        atom_number = 0
        number_of_atoms_line = False
        comment_line = False
        coordinate_line = False

        # print files
        for line in crest_xyz_file:
            line_number = line_number + 1

            # checks for the beginning of each xyz entry
            if len(line.split()) == 1 and is_positive_integer(line.split()[0]):
                coordinate_line = False
                number_of_atoms_line = True

            if number_of_atoms_line:
                # prints the end of the previous .inp file, if there is one, and closes it
                if conformer_number != 0:
                    print("*", file=output_file)
                    output_file.close()

                # increment conformer_number and open a new file
                conformer_number = conformer_number + 1
                output_file = open('s2-sp/s2_{}_sp_svp.inp'.format(conformer_number), 'w')

                # output a running counter to stdout occasionally
                if conformer_number % 100 == 0:
                    print("{}...".format(conformer_number))

                # reset atom_number
                atom_number = 0

                # print the header of each input file
                print(keyword_line, file=output_file)
                print("", file=output_file)
                print("* xyz 0 1", file=output_file)

                # tell the script what's going to happen next, and skip to the next line of the xyz file
                number_of_atoms_line = False
                comment_line = True
                continue

            if comment_line:
                # don't really want to do anything with this, so just set the variables and continue
                comment_line = False
                coordinate_line = True
                continue

            if coordinate_line:
                # increments atom_number and prints it to the .inp file
                atom_number = atom_number + 1
                if atom_number <= atoms_to_keep:
                    print(line.rstrip("\n"), file=output_file)

        # prints the end of the last .inp file and closes it
        print("*", file=output_file)
        output_file.close()
        print("{} input files generated.".format(conformer_number))
        print()
