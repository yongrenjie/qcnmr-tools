#!/usr/bin/env python3

import sys
import os
import re

def determine_allxyz_file():
    allxyz_file = '.allxyz file'
    if len(sys.argv) == 2:
        allxyz_file = sys.argv[1]
    else:
        for file in os.listdir(os.getcwd()):
            if file.endswith('.ensemble.allxyz'):
                allxyz_file = file
    return allxyz_file

def main():
    try:
        allxyz_file = determine_allxyz_file()
        allxyz_file_name = allxyz_file.rstrip(".allxyz")
        input_file = open(allxyz_file,'r')
        print("Converting {}...".format(allxyz_file))

        keywords = ('! OPT PAL4 PBEh-3c CPCM(Chloroform)\n'
                    '%base "opt"\n'
                    '%scf MaxIter 500 end\n\n'
                    '*xyz 0 1\n')

        conformer_number = 1
        output_file = open('{}_conf{}.inp'.format(allxyz_file_name, conformer_number), 'w')
        output_file.write(keywords)
        for line in input_file:
            if '>' in line:
                output_file.write("*\n")
                output_file.close()
                conformer_number = conformer_number + 1
                output_file = open('{}_conf{}.inp'.format(allxyz_file_name, conformer_number), 'w')
                output_file.write(keywords)
            else:
                number_atoms_line = re.match(r'\s+\d+', line)
                energies_line = re.match(r'\s+-*\d+.\d+', line)
                if line.strip() and not number_atoms_line and not energies_line:
                    output_file.write(line.rstrip("\n"))
                    output_file.write("\n")
        output_file.write("*\n")
        output_file.close()
        input_file.close()

    except IOError or FileNotFoundError:
        print("{} not found".format(allxyz_file))

main()