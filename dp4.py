#!/usr/bin/env python3

import pandas as pd
from scipy import stats

# define degrees of freedom and standard deviations for t-distributions, as reported in main text of paper
DF_1H = 14.18
SD_1H = 0.185
DF_13C = 11.38
SD_13C = 2.306


def error_quit(error_message):
    print()
    print("ERROR: {}".format(error_message))
    print("Exiting...")
    sys.exit()
    return 0


def fmt_float(fl):
    if -0.000001 < fl < 0.000001 and fl != 0:
        return "{:10.2e}".format(fl)
    else:
        return "{:10.6f}".format(fl)


def calculate_dp4_probability(atoms, expt, calc):
    """
    Returns the product of probabilities of observing the errors in chemical shifts, i.e. P of getting the calculated
    shifts given the experimental shifts, or P(DP4|A) where A is a specific assignment.
    More precisely, this returns a list of the 13C, 1H, and combined DP4 probabilities, in that order.
    """

    # generate sub-series for 13C and 1H chemical shifts from the overall series
    carbons = []
    hydrogens = []
    for index, atom in atoms.iteritems():
        if atom == "C" or index == "c":
            carbons.append(index)
        elif atom == "H" or index == "h":
            hydrogens.append(index)
    expt_c = expt[carbons]
    expt_h = expt[hydrogens]
    calc_c = calc[carbons]
    calc_h = calc[hydrogens]

    # perform empirical scaling of shifts. Calculated shifts are y-axis (slightly counterintuitive)
    c_slope, c_intercept, x4, x5, x6 = stats.linregress(expt_c, calc_c)
    h_slope, h_intercept, x7, x8, x9 = stats.linregress(expt_h, calc_h)
    scaled_calc_c = (calc_c - c_intercept)/c_slope
    scaled_calc_c.name = "scaled_calc_c"
    scaled_calc_h = (calc_h - h_intercept)/h_slope
    scaled_calc_h.name = "scaled_calc_h"

    # calculate errors
    c_errors = abs(expt_c - scaled_calc_c)
    c_errors.name = "c_errors"
    h_errors = abs(expt_h - scaled_calc_h)
    h_errors.name = "h_errors"

    # calculate probabilities
    c_probs = 1 - stats.t.cdf(c_errors, DF_13C, loc=0, scale=SD_13C)
    h_probs = 1 - stats.t.cdf(h_errors, DF_1H, loc=0, scale=SD_1H)
    total_c_prob = c_probs.prod()
    total_h_prob = h_probs.prod()
    total_combined_prob = total_c_prob * total_h_prob

    return [total_c_prob, total_h_prob, total_combined_prob]


def dp4(atoms, expt, calc_df):

    number_of_isomers = len(calc_df.columns) - 2
    p_c_dp4_given_isomer = []
    p_h_dp4_given_isomer = []
    p_combined_dp4_given_isomer = []
    p_isomer_given_c_dp4 = []
    p_isomer_given_h_dp4 = []
    p_isomer_given_combined_dp4 = []

    print()
    print("==============================")
    print("DP4 ANALYSIS: {}".format(expt.name))
    print("==============================")
    print()

    # calculate P(DP4|isomer)
    for j in range(number_of_isomers):
        c_prob, h_prob, combined_prob = calculate_dp4_probability(atoms, expt, calc_df.iloc[:, j + 2])
        p_c_dp4_given_isomer.append(c_prob)
        p_h_dp4_given_isomer.append(h_prob)
        p_combined_dp4_given_isomer.append(combined_prob)

    # convert to P(isomer|DP4)
    for k in range(number_of_isomers):
        p_isomer_given_c_dp4.append(p_c_dp4_given_isomer[k] / sum(p_c_dp4_given_isomer))
        p_isomer_given_h_dp4.append(p_h_dp4_given_isomer[k] / sum(p_h_dp4_given_isomer))
        p_isomer_given_combined_dp4.append(p_combined_dp4_given_isomer[k] / sum(p_combined_dp4_given_isomer))
        print("ASSIGNMENT {} : {} ==> {}".format(k + 1, expt.name, calc_df.iloc[:, k + 2].name))
        print("------------------------------------")
        print("13C      : {}".format(fmt_float(p_isomer_given_c_dp4[k])))
        print("1H       : {}".format(fmt_float(p_isomer_given_h_dp4[k])))
        print("Combined : {}".format(fmt_float(p_isomer_given_combined_dp4[k])))
        print()

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
        dp4(expt_df['atom'], expt_df.iloc[:, i + 2], calc_df)

    print("Please cite: Smith, S. G.; Goodman, J. M. J. Am. Chem. Soc. 2010, 132 (37), 12946–12959.")
