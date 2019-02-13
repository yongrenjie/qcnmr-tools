import sys
import os

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
        conformer_number = 1
        output_file = open('{}_conf{}.xyz'.format(allxyz_file_name, conformer_number), 'w')
        for line in input_file:
            if '>' in line:
                output_file.close()
                conformer_number = conformer_number + 1
                output_file = open('{}_conf{}.xyz'.format(allxyz_file_name, conformer_number), 'w')
            else:
                output_file.write(line)
        output_file.close()
        input_file.close()

        input_file = open(allxyz_file,'r')
        trj_file = open('{}_conf_all.xyz'.format(allxyz_file_name),'w')
        for line in input_file:
            if '>' not in line:
                trj_file.write(line.lstrip())
        trj_file.close()
        trj_file.close()

    except IOError or FileNotFoundError:
        print("{} not found".format(allxyz_file))

main()