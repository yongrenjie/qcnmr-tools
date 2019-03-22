#!/usr/bin/env python3

import sys
import pandas as pd


def cp3(atoms, calc_a, calc_b, expt_a, expt_b):
    print("ASSIGNMENT: ({}, {}) -> ({}, {})".format(expt_a.name, expt_b.name, calc_a.name, calc_b.name))
    Delta_c = calc_a - calc_b
    Delta_e = expt_a - expt_b

    Dc_divide_De = pd.Series(Delta_c / Delta_e > 1)     # logical array
    sum_f3 = ((((Delta_e ** 3) / Delta_c) * Dc_divide_De) + ((Delta_e * Delta_c) * (1 - Dc_divide_De))).sum()
    sum_DeSquared = (Delta_e ** 2).sum()

    cp3_combined = sum_f3 / sum_DeSquared
    print("Combined CP3: {}".format(cp3_combined))

    return cp3_combined


def parse_data(filename):
    with open(filename, "r") as file:

        line_number = 0
        data = []

        for line in file:
            line_number = line_number + 1
            if line_number == 1:
                names = ["label", "atom"] + line.split()    # gets names of the isomers from header line
            if line_number > 1 and line.strip():     # gets shifts from lines below, rejecting whitespace lines
                line_data = [line.split()[0], line.split()[0][0]] + [float(i) for i in line.split()[1:]]
                data.append(line_data)

        return pd.DataFrame(data, columns=names)


if __name__ == '__main__':
    print()
    print("PLEASE CITE: Smith, S. G.; Goodman, J. M. J. Org. Chem. 2009, 74 (12), 4597–4607.")
    print()

    calc_df = parse_data("calc.txt")
    expt_df = parse_data("expt.txt")

    print("===============")
    print("CALCULATED DATA")
    print("===============")
    print(calc_df)
    print()
    print("=================")
    print("EXPERIMENTAL DATA")
    print("=================")
    print(expt_df)

    number_of_isomers = len(calc_df.columns) - 2   # 2

    for i in range(number_of_isomers): # 0, 1
        for j in range(number_of_isomers):
            if j > i:
                print()
                print("==================================================")
                # calculate CP3 for the first way round ("correct")
                cp3_correct = cp3(calc_df['atom'], calc_df.iloc[:, i+2], calc_df.iloc[:, j+2],
                                  expt_df.iloc[:, i+2], expt_df.iloc[:, j+2])
                # calculate CP3 for the other way round ("incorrect")
                cp3_incorrect = cp3(calc_df['atom'], calc_df.iloc[:, i+2], calc_df.iloc[:, j+2],
                                    expt_df.iloc[:, j+2], expt_df.iloc[:, i+2])



