#!/usr/bin/env python3

import re
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("crestname", action='store', help='crest_conformers.xyz file')
    parser.add_argument("csvname", action='store', help='csv file to filter conformers by')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    crest_file = args.crestname
    csv_file = args.csvname

    keywords = "! TPSS def2-SVP D3BJ CPCM(Methanol) PAL4 Opt NumFreq"

    allowed_conformers = []
    with open(csv_file, 'r') as filter_file:
        line_number = 0
        for line in filter_file:
            line_number = line_number + 1
            if line_number > 1:
                allowed_conformers.append(int(line.split(",")[1]))
    print(allowed_conformers)

    with open(crest_file, 'r') as crest_xyz_file:
        line_number = 0
        conformer_number = 0

        for line in crest_xyz_file:
            line_number = line_number + 1
            number_of_atoms_found = re.match(r'^\s+(\d+)\s+$', line)
            energy_found = re.match(r'^\s+(-\d+.\d+)\s+$', line)

            if number_of_atoms_found:
                conformer_number = conformer_number + 1
                if conformer_number == allowed_conformers[0]:
                    output_file = open("tpss_svp_opt_{}.inp".format(conformer_number), 'w')
                elif conformer_number in allowed_conformers:
                    print("*", file=output_file)
                    output_file.close()
                    output_file = open("tpss_svp_opt_{}.inp".format(conformer_number), 'w')

            if conformer_number in allowed_conformers:
                if number_of_atoms_found:
                    print(keywords, file=output_file)
                    print("", file=output_file)
                elif energy_found:
                    print("#  Conf {}; GFN-xTB: {}".format(conformer_number, energy_found.group(1)), file=output_file)
                    print("* xyz 0 1", file=output_file)
                else:
                    print(line.rstrip("\n"), file=output_file)

        print("*", file=output_file)
        output_file.close()