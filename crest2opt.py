#!/usr/bin/env python3

import re
import argparse
import os
import sys


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-cr", "--crestfile", action='store', default='../s1-crest/crest_conformers.xyz',
                        help='crest_conformers.xyz file (default) ../s1-crest/crest_conformers.xyz')
    parser.add_argument("-cs", "--csvfile", action='store', default='../s2-sp/sp_filtered_conformers.csv',
                        help='csv file to filter conformers by (default ../s2-sp/sp_filtered_conformers.csv')
    parser.add_argument("--remove", action="store", type=int, default=0,
                        help="Number of atoms to remove from the end of each set of coordinates")
    parser.add_argument("-a", "--atoms", action="store", type=int,
                        help="Number of atoms to optimise (everything else will be constrained)")
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
    crest_file = args.crestfile
    csv_file = args.csvfile

    # set ORCA keyword line depending on user input
    default_keyword_line = "! TPSS def2-SVP D3BJ CPCM(Methanol) Opt LooseOpt PAL8"
    keyword_line = input("The default keyword line is: {} \n"
                         "Please enter the desired keyword line, "
                         "or leave blank to use the default keywords: ".format(default_keyword_line))
    if keyword_line.strip() == "":
        keyword_line = default_keyword_line

    # Read csv file to determine which conformers pass the filter
    allowed_conformers = []
    with open(csv_file, 'r') as filter_file:
        line_number = 0
        for line in filter_file:
            line_number = line_number + 1
            if line_number > 1:
                allowed_conformers.append(int(line.split(",")[1]))
    print()
    print("Input files will be generated for {} conformers: {}".format(len(allowed_conformers), allowed_conformers))
    print()

    # determine total number of atoms
    test_file = open(crest_file, 'r')
    total_atoms = int(test_file.readline().strip())
    test_file.close()

    # construct %geom block based on atoms to be constrained
    if args.atoms:
        if args.atoms > total_atoms:
            print("Each conformer only has {} atoms. "
                  "Please specify fewer atoms than this with -a/--atoms.".format(total_atoms))
            sys.exit()
        geom_block = "%geom \n" \
                     "  Constraints\n"
        for i in range(args.atoms, total_atoms):
            geom_block = geom_block + "    {{ C {} C }}\n".format(i)
        geom_block = geom_block + "  end\nend\n"

    # make the directory
    try:
        os.mkdir("s3-opt")
    except:
        pass

    # generate ORCA optimisation input files
    with open(crest_file, 'r') as crest_xyz_file:
        # initialise variables
        line_number = 0
        conformer_number = 0
        atom_number = 0
        is_first_conformer = True
        comment_line = False
        coordinate_line = False
        number_of_atoms_line = False

        # print files
        for line in crest_xyz_file:
            line_number = line_number + 1

            # check for the beginning of each xyz entry
            if len(line.split()) == 1 and is_positive_integer(line.split()[0]):
                coordinate_line = False
                number_of_atoms_line = True

            if number_of_atoms_line:
                # increments conformer number
                conformer_number = conformer_number + 1

                # checks if the conformer number is allowed
                if conformer_number in allowed_conformers:

                    # prints the end of the previous .inp file and closes it, if there is one
                    if not is_first_conformer:
                        print("*", file=output_file)
                        output_file.close()

                    # opens a new .inp file and prints the headers if necessary
                    output_file = open("s3-opt/s3_{}_opt_svp.inp".format(conformer_number), 'w')
                    print(keyword_line, file=output_file)
                    print("", file=output_file)
                    if args.atoms:
                        print(geom_block, file=output_file)
                        print("", file=output_file)
                    print("* xyz 0 1", file=output_file)

                    # sets the flag to tell us whether it is the first .inp file
                    if is_first_conformer:
                        is_first_conformer = False

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
                if conformer_number in allowed_conformers:
                    print(line.rstrip("\n"), file=output_file)

        # print the end of the last .inp file and close it
        print("*", file=output_file)
        output_file.close()

    print("Done.")
    print()
