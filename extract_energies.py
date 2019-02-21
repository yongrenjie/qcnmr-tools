#!/usr/bin/env python3

import argparse
import matplotlib.pyplot as plt
import pandas as pd
import sys

HARTREE_TO_KCAL = 627.509

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", action='store', help='.out file(s) to analyse', nargs="*")
    parser.add_argument("-t", "--threshold", type=int, default=0, help="Finds conformers within THRESHOLD kcal/mol of the lowest energy conformer and prints them to a csv file.")
    parser.add_argument("-p", "--plot", action='store_true', help='Plot energies of all conformers.')
    parser.add_argument("-c", "--csv", action='store_true', help='Output all conformers to a csv file.')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    threshold_kcal = args.threshold

    conformer_numbers = []
    conformer_energies = []

    if len(args.filenames) == 1:
        # determine what output file we are reading (CREST or ORCA)
        output_file_determined = False
        orca_file_found = False
        output_file_type = ""
        output_file = args.filenames[0]
        while not output_file_determined:
            with open(output_file, 'r') as outputfile:
                for line in outputfile:
                    if "C R E S T" in line:
                        output_file_type = "crest"
                        output_file_determined = True
                        break
                    elif "O   R   C   A" in line:
                        orca_file_found = True
                    if orca_file_found:
                        if "|  1> ! " in line:
                            if "opt" in line.lower():
                                output_file_type = "orca_opt"
                                output_file_determined = True
                                break
                            else:
                                output_file_type = "orca_sp"
                                output_file_determined = True
                                break
                else:
                    output_file_determined = True
                    sys.exit("Could not determine output file type.")

        if output_file_type == "crest":
            energy_block = False
            with open(output_file, 'r') as outputfile:
                for line in outputfile:
                    if "number of unique conformers for further calc" in line:
                        energy_block = True
                    if line.strip().startswith("NMR mode"):
                        energy_block = False
                    if energy_block:
                        if line.split()[0].isdigit():
                            conformer_numbers.append(int(line.split()[0]))
                            conformer_energies.append(float(line.split()[1]))
            all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})

        elif output_file_type == "orca_sp":
            with open(output_file, 'r') as outputfile:
                conformer_number = 0
                for line in outputfile:
                    if "MULTIPLE XYZ STEP" in line:
                        conformer_number = conformer_number + 1
                        conformer_numbers.append(conformer_number)
                    if "FINAL SINGLE POINT ENERGY" in line:
                        conformer_energies.append(float(line.split()[-1]))

            all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})
            all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL

        elif output_file_type == "orca_opt":
            print("opt file found")
            with open(output_file, 'r') as outputfile:
                conformer_number = 0
                converged = False
                for line in outputfile:
                    if "FINAL ENERGY EVALUATION AT THE STATIONARY POINT" in line:
                        converged = True
                    if "MULTIPLE XYZ OPTIMIZATION STRUCTURE" in line:
                        converged = False
                        conformer_number = conformer_number + 1
                        conformer_numbers.append(conformer_number)
                    if converged and "FINAL SINGLE POINT ENERGY" in line:
                        conformer_energies.append(float(line.split()[-1]))

            all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})
            all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL

    else:
        test_file = args.filenames[0]
        with open(test_file, 'r') as determine_output_file:
            for line in determine_output_file:
                if "|  1> ! " in line:
                    if "opt" in line.lower():
                        output_file_type = "multiple_orca_opt"
                        output_file_determined = True
                        break
                    else:
                        output_file_type = "multiple_orca_sp"
                        output_file_determined = True
                        break

        if output_file_type == "multiple_orca_opt":
            for file in args.filenames:
                with open(file, 'r') as opt_output_file:
                    conformer_numbers.append(int(file.split(".")[-2].split("_")[-1]))  # gets number from file name
                    converged = False
                    for line in opt_output_file:
                        if "FINAL ENERGY EVALUATION AT THE STATIONARY POINT" in line:
                            converged = True
                        if converged and "FINAL SINGLE POINT ENERGY" in line:
                            conformer_energies.append(float(line.split()[-1]))
                            break
            all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})
            all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL
            all_conformers = all_conformers.sort_values('num')
            all_conformers = all_conformers.reset_index(drop=True)
        elif output_file_type == "multiple_orca_sp":
            for file in args.filenames:
                with open(file, 'r') as sp_output_file:
                    conformer_numbers.append(int(file.split(".")[-2].split("_")[-1])) # gets number from file name
                    for line in sp_output_file:
                        if "FINAL SINGLE POINT ENERGY" in line:
                            conformer_energies.append(float(line.split()[-1]))
            all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})
            all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL
            all_conformers = all_conformers.sort_values('num')
            all_conformers = all_conformers.reset_index(drop=True)

    print(all_conformers)

    if args.plot:
        all_conformers.plot(x='num', y='energy', kind='line')
        plt.xlabel("Conformer number")
        plt.ylabel("Energy (kcal/mol relative to lowest)")
        plt.show()

    if args.threshold > 0:
        threshold_kcal = args.threshold
        filtered_conformers = all_conformers[all_conformers['energy'] <= threshold_kcal]
        filtered_conformers = filtered_conformers.sort_values('num')
        filtered_conformers = filtered_conformers.reset_index(drop=True)
        print(filtered_conformers)

        if output_file_type in ["orca_sp", "multiple_orca_sp"]:
            csv_filename = "sp_filtered_conformers.csv"
        elif output_file_type in ["orca_opt", "multiple_orca_opt"]:
            csv_filename = "opt_filtered_conformers.csv"
        else:
            csv_filename = "filtered_conformers.csv"
        filtered_conformers.to_csv(csv_filename, columns=['num', 'energy'])
        print("Conformers within {} kcal/mol written to {}.".format(threshold_kcal, csv_filename))

    if args.csv:
        if output_file_type in ["orca_sp", "multiple_orca_sp"]:
            csv_filename = "sp_all_conformers.csv"
        elif output_file_type in ["orca_opt", "multiple_orca_opt"]:
            csv_filename = "opt_all_conformers.csv"
        else:
            csv_filename = "all_conformers.csv"
        all_conformers.to_csv(csv_filename, columns=['num', 'energy'])
        print("All conformers written to {}.".format(csv_filename))
