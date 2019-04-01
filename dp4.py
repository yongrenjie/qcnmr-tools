#!/usr/bin/env python3

import pandas as pd
import random


def error_quit(error_message):
    print()
    print("ERROR: {}".format(error_message))
    print("Exiting...")
    sys.exit()
    return 0


def calculate_dp4_probability(expt, calc):
    return random.randint(1,10000)/10000      # something needs to change here...


def dp4(expt, calc_df):

    number_of_isomers = len(calc_df.columns) - 2
    p_dp4_given_isomer = []
    p_isomer_given_dp4 = []

    print()
    print("DP4 analysis for {}".format(expt.name))

    for j in range(number_of_isomers):
        print("comparing {} against {}...".format(expt.name, calc_df.iloc[:, j + 2].name))
        p_dp4_given_isomer.append(calculate_dp4_probability(expt.name, calc_df.iloc[:, j + 2].name))

    # convert to P(isomer|DP4)
    for k in range(number_of_isomers):
        p_isomer_given_dp4.append(p_dp4_given_isomer[k] / sum(p_dp4_given_isomer))
        print("P({} ==> {}): {}".format(expt.name, calc_df.iloc[:, k + 2].name, p_isomer_given_dp4[k]))

    return 0


def parse_data(filename):
    with open(filename, "r") as file:
        line_number = 0
        data = []

        for line in file:
            line_number = line_number + 1
            # gets names of the isomers from header line
            if line_number == 1:
                names = ["label", "atom"] + line.split()
            # gets shifts from lines below, rejecting whitespace and comments
            if line_number > 1 and line.strip() and not line.strip().startswith("#"):
                if not (len(line.split()) - 1 == len(names) - 2):
                    error_quit("Number of shifts in line {} of {} does not "
                               "match the number of names given.".format(line_number, filename))
                line_data = [line.split()[0], line.split()[0][0]] + [float(i) for i in line.split()[1:]]
                data.append(line_data)

        return pd.DataFrame(data, columns=names)


if __name__ == '__main__':
    calc_df = parse_data("dp4_calc.txt")
    expt_df = parse_data("dp4_expt.txt")

    # check for invalid number of columns
    if len(calc_df.columns) < 4:
        error_quit("Please provide at least two sets of calculated shifts for DP4 analysis.")
    if len(expt_df.columns) < 3:
        error_quit("Please provide at least one set of experimental shifts for DP4 analysis.")

    print("===============")
    print("CALCULATED DATA")
    print("===============")
    print(calc_df)
    print()
    print("=================")
    print("EXPERIMENTAL DATA")
    print("=================")
    print(expt_df)

    # check for invalid rows in chemical shift data
    for i in range(len(calc_df)):
        if not calc_df['label'][i] == expt_df['label'][i]:
            error_quit("Atom labels {} in dp4_calc.txt and {} in dp4_expt.txt do not match.".format(calc_df['label'][i],
                                                                                                    expt_df['label'][i]))
        if calc_df['atom'][i] not in ["C", "c", "H", "h"]:
            error_quit("Atom label {} in dp4_calc.txt does not begin with C/c/H/H.".format(calc_df['label'][i]))
        if expt_df['atom'][i] not in ["C", "c", "H", "h"]:
            error_quit("Atom label {} in dp4_expt.txt does not begin with C/c/H/H.".format(expt_df['label'][i]))

    for i in range(len(expt_df.columns) - 2):
        dp4(expt_df.iloc[:, i + 2], calc_df)

    print()
    print("Please cite: Smith, S. G.; Goodman, J. M. J. Am. Chem. Soc. 2010, 132 (37), 12946–12959.")
