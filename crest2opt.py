#!/usr/bin/env python3

import re
import argparse
import os

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-cr", "--crestfile", action='store', default='crest_conformers.xyz',
                        help='crest_conformers.xyz file (default) crest_conformers.xyz')
    parser.add_argument("-cs", "--csvfile", action='store', default='../s2-sp/sp_filtered_conformers.csv',
                        help='csv file to filter conformers by (default ../s2-sp/sp_filtered_conformers.csv')
    parser.add_argument("--remove", action="store", type=int, default=0,
                        help="Number of atoms to remove from the end of each set of coordinates")
    parser.add_argument("--constrain", action="store", type=int,
                        help="Number of atoms at the end of each set of coordinates to constrain during optimisation")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    crest_file = args.crestname
    csv_file = args.csvname

    # set ORCA keyword line depending on user input
    default_keyword_line = "! TPSS def2-SVP D3BJ CPCM(Methanol) Opt LooseOpt PAL8"
    keyword_line = input("The default keyword line is: {} \n"
                         "Please enter the desired keyword line, "
                         "or leave blank to use the default keywords: ".format(default_keyword_line))
    if keyword_line.strip() == "":
        keyword_line = default_keyword_line

    allowed_conformers = []
    allowed_conformer_energies = []
    with open(csv_file, 'r') as filter_file:
        line_number = 0
        for line in filter_file:
            line_number = line_number + 1
            if line_number > 1:
                allowed_conformers.append(int(line.split(",")[1]))
                allowed_conformer_energies.append(float(line.split(",")[2]))
    print()
    print("Input files will be generated for {} conformers: {}".format(len(allowed_conformers), allowed_conformers))
    if args.freq:
        print("Frequency calculation requested.")
    print()

    # determine total number of atoms
    test_file = open(crest_file, 'r')
    total_atoms = int(test_file.readline().strip())
    test_file.close()

    if args.constrain:
        geom_block = "%geom \n" \
                     "  Constraints\n"
        for i in range(args.constrain):
            geom_block = geom_block + "    {{ C {} C }}\n".format(i + total_atoms - args.constrain)
        geom_block = geom_block + "  end\nend\n"

    try:
        os.mkdir("s3-opt")
    except:
        pass

    with open(crest_file, 'r') as crest_xyz_file:
        line_number = 0
        conformer_number = 0
        atom_number = 0

        for line in crest_xyz_file:
            line_number = line_number + 1
            number_of_atoms_found = re.match(r'^\s+(\d+)\s+$', line)
            energy_found = re.match(r'^\s+(-\d+.\d+)\s+$', line)

            if number_of_atoms_found:
                conformer_number = conformer_number + 1
                if conformer_number == allowed_conformers[0]:
                    output_file = open("s3-opt/s3_{}_opt_svp.inp".format(conformer_number), 'w')
                elif conformer_number in allowed_conformers:
                    print("*", file=output_file)
                    output_file.close()
                    output_file = open("s3-opt/s3_{}_opt_svp.inp".format(conformer_number), 'w')

            if conformer_number in allowed_conformers:
                if number_of_atoms_found:
                    atom_number = 0
                    print(keyword_line, file=output_file)
                    print("", file=output_file)
                    if args.constrain:
                        print(geom_block, file=output_file)
                        print("", file=output_file)
                elif energy_found:
                    print("#  Conf {}".format(conformer_number), file=output_file)
                    print("#  S1-CREST: {}".format(energy_found.group(1)), file=output_file)
                    print("#  S2-SP: {}".format(allowed_conformer_energies[allowed_conformers.index(conformer_number)]), file=output_file)
                    print("* xyz 0 1", file=output_file)
                else:
                    if atom_number < total_atoms - args.remove:
                        print(line.rstrip("\n"), file=output_file)
                    atom_number = atom_number + 1

        print("*", file=output_file)
        output_file.close()

    print("Done.")
    print()