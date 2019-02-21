#!/usr/bin/env python3

import re
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", action='store', help='crest_conformers.xyz file')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    conformer_file = args.filename
    output_allxyz_file = conformer_file.replace('.xyz', '.allxyz')
    input_file = open(conformer_file, 'r')
    print("Converting {}...".format(conformer_file))
    with open('crest_conformers.allxyz', 'w') as allxyz_file:
        line_number = 0
        for line in input_file:
            line_number = line_number + 1
            number_of_atoms_found = re.match(r'\s+(\d+)\s+', line)
            energy_found = re.match(r'\s+(-\d+.\d+)\s+', line)
            if line_number > 1 and number_of_atoms_found:
                print(">", file=allxyz_file)
                print(line.rstrip("\n"), file=allxyz_file)
            elif energy_found:
                print("   GFN-xTB: {}".format(energy_found.group(1)), file=allxyz_file)
            else:
                print(line.rstrip("\n"), file=allxyz_file)
    print("Done.")