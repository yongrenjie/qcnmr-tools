import sys
import os
import re

def main():
    try:
        conformer_file = ""
        conformer_file = sys.argv[1]
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
                    print("   GFN-xTB energy (GBSA MeOH): {}".format(energy_found.group(1)), file=allxyz_file)
                else:
                    print(line.rstrip("\n"), file=allxyz_file)
        input_file.close()
        print("Done.")

    except IOError or FileNotFoundError:
        print("{} not found".format(allxyz_file))

main()
