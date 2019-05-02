#!/usr/bin/env python3

import argparse
import numpy as np
import pandas as pd
import sys

HARTREE_TO_KCAL = 627.509474
KT_298_K = 0.592186673

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", action='store', help='.out file(s) to analyse', nargs="*")
    parser.add_argument("-t", "--threshold", type=float, default=0,
                        help="Finds conformers within X kcal/mol of the lowest "
                             "energy conformer and prints them to a csv file.")
    parser.add_argument("-c", "--csv", action='store_true', help='Output all conformers to a csv file.')
    parser.add_argument("-p", "--population", type=int, default=0,
                        help="Calculates Boltzmann populations (assumes no degeneracy), "
                             "selects the lowest-energy X% of conformers, prints numbers/populations to a csv file.")
    parser.add_argument("--gibbs", action="store_true", help="Weight using Gibbs free energies.")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    threshold_kcal = args.threshold

    if args.gibbs:
        energy_string = "Final Gibbs free enthalpy"
        energy_index = -2
    else:
        energy_string = "FINAL SINGLE POINT ENERGY"
        energy_index = -1

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
                    if energy_string in line:
                        conformer_energies.append(float(line.split()[energy_index]))

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
                    if converged and energy_string in line:
                        conformer_energies.append(float(line.split()[energy_index]))

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
                    conformer_numbers.append(int(file.split(".")[-2].split("_")[1]))  # gets number from file name
                    converged = False
                    for line in opt_output_file:
                        if "FINAL ENERGY EVALUATION AT THE STATIONARY POINT" in line:
                            converged = True
                        if converged and energy_string in line:
                            conformer_energies.append(float(line.split()[energy_index]))
                            break
            all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})
            all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL
            all_conformers = all_conformers.sort_values('num')
            all_conformers = all_conformers.reset_index(drop=True)
        elif output_file_type == "multiple_orca_sp":
            for file in args.filenames:
                with open(file, 'r') as sp_output_file:
                    conformer_numbers.append(int(file.split(".")[-2].split("_")[1])) # gets number from file name
                    for line in sp_output_file:
                        if energy_string in line:
                            conformer_energies.append(float(line.split()[energy_index]))
            all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})
            all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL
            all_conformers = all_conformers.sort_values('num')
            all_conformers = all_conformers.reset_index(drop=True)
    print("All conformers: ")
    print(all_conformers)
    print()

    if args.threshold > 0:
        threshold_kcal = args.threshold
        filtered_conformers = all_conformers[all_conformers['energy'] <= threshold_kcal].copy()
        filtered_conformers = filtered_conformers.sort_values('num')
        filtered_conformers = filtered_conformers.reset_index(drop=True)
        print("Conformers below {} kcal/mol:".format(threshold_kcal))
        print(filtered_conformers)

        if output_file_type in ["orca_sp", "multiple_orca_sp"]:
            csv_filename = "sp_filtered_conformers.csv"
        elif output_file_type in ["orca_opt", "multiple_orca_opt"]:
            csv_filename = "opt_filtered_conformers.csv"
        else:
            csv_filename = "filtered_conformers.csv"
        filtered_conformers.to_csv(csv_filename)
        print("Filtered conformers written to {}.".format(csv_filename))

    if args.csv:
        if output_file_type in ["orca_sp", "multiple_orca_sp"]:
            csv_filename = "sp_all_conformers.csv"
        elif output_file_type in ["orca_opt", "multiple_orca_opt"]:
            csv_filename = "opt_all_conformers.csv"
        else:
            csv_filename = "all_conformers.csv"
        all_conformers.to_csv(csv_filename)
        print("All conformers written to {}.".format(csv_filename))

    if args.population > 0:
        all_conformers['boltzmann'] = np.exp(-all_conformers['energy']/KT_298_K)
        partition_function = all_conformers['boltzmann'].sum()
        all_conformers['population'] = all_conformers['boltzmann']/partition_function

        all_conformers = all_conformers.sort_values('population', ascending=False)
        all_conformers = all_conformers.reset_index(drop=True)
        all_conformers["cumul_pop"] = 0
        threshold_reached = False
        for i in range(len(all_conformers.index)):
            cumulative_population = all_conformers.loc[0:i, "population"].sum()
            if threshold_reached:
                all_conformers.loc[i, "cumul_pop"] = 10
            else:
                all_conformers.loc[i, "cumul_pop"] = cumulative_population
                if cumulative_population > args.population/100:
                    threshold_reached = True
        filtered_conformers = all_conformers[all_conformers["cumul_pop"] < 10].copy()
        # .copy() not strictly needed, but overcomes the pandas SettingWithCopyWarning
        filtered_conformers["renorm_pop"] = filtered_conformers["population"]/filtered_conformers["population"].sum()
        print(filtered_conformers)
        csv_filename = "nmr_filtered_conformers.csv"
        filtered_conformers.to_csv(csv_filename)
        print("Filtered conformers written to {}.".format(csv_filename))