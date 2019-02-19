#!/usr/bin/env python3

import re
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", action='store', help='crest_conformers.xyz file')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    crest_file = args.filename

    with open(crest_file, 'r') as crest_xyz_file:
        line_number = 0
        conformer_number = 0
        output_file_number = 1
        check_output_number = True
        output_file = open('crest_conformers{}.allxyz'.format(output_file_number), 'w')
        for line in crest_xyz_file:
            line_number = line_number + 1
            number_of_atoms_found = re.match(r'\s+(\d+)\s+', line)
            energy_found = re.match(r'\s+(-\d+.\d+)\s+', line)
            if number_of_atoms_found:
                conformer_number = conformer_number + 1
                check_output_number = True
            if (conformer_number-1) % 50 == 0 and check_output_number and conformer_number != 1:
                output_file.close()
                output_file_number = output_file_number + 1
                output_file = open('crest_conformers{}.allxyz'.format(output_file_number), 'w')
                check_output_number = False
            if line_number > 1 and number_of_atoms_found:
                print(">", file=output_file)
                print(line.rstrip("\n"), file=output_file)
            elif energy_found:
                print("   GFN-xTB: {}".format(energy_found.group(1)), file=output_file)
            else:
                print(line.rstrip("\n"), file=output_file)
        output_file.close()


    keywords = "! TPSS def2-SVP D3BJ CPCM(Methanol) SP PAL4"
    for i in range(output_file_number):
        sp_inp_file = "tpss_svp_sp{}.inp".format(i+1)
        with open(sp_inp_file, 'w') as sp_file:
            print(keywords, file=sp_file)
            print("", file=sp_file)
            print("*xyzfile 0 1 crest_conformers{}.allxyz".format(i+1), file=sp_file)
            print("", file=sp_file)
