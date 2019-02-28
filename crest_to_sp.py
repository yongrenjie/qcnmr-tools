#!/usr/bin/env python3

import re
import argparse
import os
import sys

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help='File containing all conformers (default crest_conformers.xyz)')
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

    keywords = "! TPSS def2-SVP D3BJ CPCM(Methanol) PAL4 SP"

    try:
        os.mkdir("s2-sp")
    except:
        pass

    try:
        with open(crest_file, 'r') as crest_xyz_file:
            line_number = 0
            conformer_number = 1
            output_file = open('s2-sp/s2_{}_sp_svp.inp'.format(conformer_number), 'w')
            for line in crest_xyz_file:
                line_number = line_number + 1
                number_of_atoms_found = re.match(r'\s+(\d+)\s+', line)
                energy_found = re.match(r'\s+(-\d+.\d+)\s+', line)
                if number_of_atoms_found:
                    if line_number > 1:
                        print("*", file=output_file)
                        output_file.close()
                        if conformer_number % 100 == 0:
                            print(conformer_number)
                        conformer_number = conformer_number + 1
                        output_file = open('s2-sp/s2_{}_sp_svp.inp'.format(conformer_number), 'w')
                    print(keywords, file=output_file)
                    print("", file=output_file)
                elif energy_found:
                    print("#   GFN-xTB: {}".format(energy_found.group(1)), file=output_file)
                    print("* xyz 0 1", file=output_file)
                else:
                    print(line.rstrip("\n"), file=output_file)
            print("*", file=output_file)
            output_file.close()
            print("{} input files generated.".format(conformer_number))
            print()
    except:
        print("Please provide a valid xyz file with all conformers.")
        print()
