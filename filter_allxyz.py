import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_filename", action='store', help='.csv file which contains list of conformers to select')
    parser.add_argument("allxyz_filename", action='store', help='.allxyz file containing all conformers')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    csv_file = args.csv_filename
    allxyz_file = args.allxyz_filename
    output_allxyz_file = allxyz_file.replace(".allxyz", "_filtered.allxyz")

    filtered_conformer_numbers = []
    filtered_conformer_energies = []

    with open(csv_file, 'r') as list_of_conformers:
        for line in list_of_conformers:
            if not line.lstrip().startswith(","):
                filtered_conformer_numbers.append(int(line.rstrip("\n").split(",")[1]))
                filtered_conformer_energies.append(float(line.rstrip("\n").split(",")[-1]))
    print()
    print("List of accepted conformers: {}".format(sorted(filtered_conformer_numbers)))
    print()
    
    with open(allxyz_file, 'r') as unfiltered_allxyz:
        conformer_count = 1
        comment_line = False
        filtered_allxyz = open(output_allxyz_file, 'w')
        for line in unfiltered_allxyz:
            if line.strip() == ">":
                conformer_count = conformer_count + 1
            if conformer_count in filtered_conformer_numbers:
                if comment_line:
                    print("    Conformer {}; {}".format(conformer_count, line.strip()), file=filtered_allxyz)
                    comment_line = False
                elif line.strip().isdigit():
                    print(line.rstrip("\n"), file=filtered_allxyz)
                    comment_line = True
                elif not (line.strip() == ">" and conformer_count == min(filtered_conformer_numbers)):
                    print(line.rstrip("\n"), file=filtered_allxyz)
        filtered_allxyz.close()
