import re
import numpy as np
import os
import sys

def is_are(number):
    if number == 1:
        return ("is","")
    else:
        return ("are","s")

def determine_output_file():
    output_file = ''
    if len(sys.argv) == 2:
        output_file = sys.argv[1]
    else:
        for file in os.listdir(os.getcwd()):
            if file.endswith('.inp') and not file.endswith('anmr.inp') and not file.endswith('confscript.inp'):
                output_file = file.rstrip('inp') + 'out'
    return output_file

def parse_data(output_file):

    carbon_atom_labels = []
    carbon_shieldings = []
    proton_atom_labels = []
    proton_nuclide_count  = []
    proton_shifts = []
    proton_shift_uncertainties = []
    conformer = []
    population = []
    total_carbons = 0
    total_protons = 0
    total_conformers = 0

    anmr_conformer_count = 0

    with open(output_file,'r') as file:
        summary_block_state = False
        anmr_label_block_state = False
        anmr_shifts_block_state = False
        conformer_number = 0
        conformer_population = 0

        line_number = 0

        for line in file:
            line_number = line_number + 1
            conformer_found = re.match(r'Structure\s+(\d+) with population (\d+.\d+):', line)

            if conformer_found:
                conformer_number = conformer_found.group(1)
                conformer_population = conformer_found.group(2)

            if "CHEMICAL SHIELDING SUMMARY" in line:
                summary_block_state = True
                total_conformers = total_conformers + 1
            elif "MULTIPLE XYZ" in line:
                summary_block_state = False

            if summary_block_state:
                carbon_found = re.match(r'\s+(\d+)\s+C\s+(-*\d+.\d+)', line)
                if carbon_found:
                    conformer.append(int(conformer_number))
                    population.append(float(conformer_population))
                    carbon_atom_labels.append(int(carbon_found.group(1)))
                    carbon_shieldings.append(float(carbon_found.group(2)))
                    if total_conformers == 1:       # don't double count number of carbons
                        total_carbons = total_carbons + 1

            if "reading J/sigma data for conformer" in line:
                anmr_label_block_state = True
                anmr_conformer_count = anmr_conformer_count + 1
            elif "MATRIX PRINTED:" in line:
                anmr_label_block_state = False
                anmr_shifts_block_state = False
            if anmr_label_block_state and anmr_conformer_count == 1:
                proton_label_found = re.match(r'\s+\d+\s+(\d+)\s+(\d+)', line)
                if proton_label_found:
                    proton_atom_labels.append(int(proton_label_found.group(1)))
                    proton_nuclide_count.append(int(proton_label_found.group(2)))
                    total_protons = total_protons + 1

            if "average over conformers" in line:
                anmr_shifts_block_state = True
            if anmr_shifts_block_state:
                proton_shift_found = re.match(r'\s+\d+\s+\d+\s+(-*\d+.\d+)\s+\+/-\s+(\d+.\d+)', line)
                if proton_shift_found:
                    proton_shifts.append(float(proton_shift_found.group(1)))
                    proton_shift_uncertainties.append(float(proton_shift_found.group(2)))

        if total_conformers == 0:
            print("No data was found in this output file.")
            print("Please try again with a different output file.")
            print("You can pass the output file name as a command line"
                  " argument when running the script, e.g.")
            print("$ python3 anmr_shieldings.py OUTPUT.out")
            return 0

        carbon_array = np.array([population,carbon_shieldings])

    print("There {} {} conformer{} to average over.".format(is_are(total_conformers)[0],
                                                           total_conformers,
                                                            is_are(total_conformers)[1]))
    print()

    print("There {} {} carbon{} in this molecule.".format(is_are(total_carbons)[0],
                                                         total_carbons,
                                                          is_are(total_carbons)[1]))

    avg_shielding_array = np.zeros(total_carbons)
    total_popul = 0
    for i in range(total_conformers):
        popul_array = carbon_array[0, i * total_carbons:(i + 1) * total_carbons]
        popul = float(popul_array[0])
        total_popul = total_popul + popul
        shiel_array = carbon_array[1, i * total_carbons:(i + 1) * total_carbons]
        conformer_contribution = np.multiply(popul_array, shiel_array)
        avg_shielding_array = np.add(avg_shielding_array, conformer_contribution)
    avg_shielding_array = avg_shielding_array/total_popul # normalisation just in case total_popul isn't 1
    carbon_label_array = np.array(carbon_atom_labels)[0:total_carbons]

    print("================================")
    print("Carbon-13")
    print("--------------------------------")
    print("Atom label     Average shielding")
    for i in range(total_carbons):
        print("{:<15d}{:.6f}".format(carbon_label_array[i],avg_shielding_array[i]))
    print("================================")

    print()
    print("There {} {} distinct proton environment{} in this molecule.".format(is_are(total_protons)[0],
                                                                               total_protons,
                                                                               is_are(total_protons)[1]))
    print("====================================================")
    print("Hydrogen-1")
    print("----------------------------------------------------")
    print("Atom label     Nuclide count    Chemical shift (ppm)")
    for i in range(total_protons):
        print("{:<15d}{:<17d}{:.3f} +/- {:.2f}".format(proton_atom_labels[i],
                                                   proton_nuclide_count[i],
                                                   proton_shifts[i],
                                                   proton_shift_uncertainties[i]))
    print("====================================================")
    print("These shifts are already referenced.\n"
          "See ORCA 4.1.0 manual section 9.35.6.4 (p 854)")

    return 1


def main():
    output_file = determine_output_file()

    if os.path.isfile(output_file):             # Check if file exists
        print("Parsing data from {}...".format(output_file))
        print()
        parse_data(output_file)
    else:
        if len(sys.argv) == 2:
            print("The output file '{}' was not found.".format(sys.argv[1]))
        else:
            print("An output file was not found.")
        print("This script searches for your input file in the "
              "working directory to identify the output file.")
        print("You can also pass the output file name as a command "
              "line argument, e.g.")
        print("$ python3 anmr_shieldings.py OUTPUT.out")

    print()

main()