#!/usr/bin/env python3

import pandas as pd
import math

COMBINED_CORRECT_MEAN = 0.512
COMBINED_CORRECT_SD = 0.209
COMBINED_INCORRECT_MEAN = -0.637
COMBINED_INCORRECT_SD = 0.499
C13_CORRECT_MEAN = 0.547
C13_CORRECT_SD = 0.253
C13_INCORRECT_MEAN = -0.487
C13_INCORRECT_SD = 0.533
H1_CORRECT_MEAN = 0.478
H1_CORRECT_SD = 0.305
H1_INCORRECT_MEAN = -0.786
H1_INCORRECT_SD = 0.835


def normal_cdf(x, mean, sd):
    return (1.0 + math.erf((x - mean)/(sd * math.sqrt(2))))/2


def calculate_cp3_value(calc_a, calc_b, expt_a, expt_b):
    Delta_c = calc_a - calc_b
    Delta_e = expt_a - expt_b

    Dc_divide_De = pd.Series(Delta_c / Delta_e > 1)     # logical array
    sum_f3 = ((((Delta_e ** 3) / Delta_c) * Dc_divide_De) + ((Delta_e * Delta_c) * (1 - Dc_divide_De))).sum()
    sum_DeSquared = (Delta_e ** 2).sum()

    cp3 = sum_f3 / sum_DeSquared
    return cp3

def cp3(atoms, calc_a, calc_b, expt_a, expt_b):
    print()
    print("==================================================")
    print()
    # calculate CP3 for assignment A (first calc column = first expt column)
    cp3_A = calculate_cp3_value(calc_a, calc_b, expt_a, expt_b)
    # calculate CP3 for assignment B (first calc column = second expt column)
    cp3_B = calculate_cp3_value(calc_a, calc_b, expt_b, expt_a)
    # calculate probability of obtaining CP3 values given that assignment A is correct
    p_cp3_given_A = min(normal_cdf(cp3_A, COMBINED_CORRECT_MEAN, COMBINED_CORRECT_SD),
                        1 - normal_cdf(cp3_A, COMBINED_CORRECT_MEAN, COMBINED_CORRECT_SD)) * \
                    min(normal_cdf(cp3_B, COMBINED_INCORRECT_MEAN, COMBINED_INCORRECT_SD),
                        1 - normal_cdf(cp3_B, COMBINED_INCORRECT_MEAN, COMBINED_INCORRECT_SD))
    # calculate probability of obtaining CP3 values given that assignment B is correct
    p_cp3_given_B = min(normal_cdf(cp3_A, COMBINED_INCORRECT_MEAN, COMBINED_INCORRECT_SD),
                        1 - normal_cdf(cp3_A, COMBINED_INCORRECT_MEAN, COMBINED_INCORRECT_SD)) * \
                    min(normal_cdf(cp3_B, COMBINED_CORRECT_MEAN, COMBINED_CORRECT_SD),
                        1 - normal_cdf(cp3_B, COMBINED_CORRECT_MEAN, COMBINED_CORRECT_SD))
    # calculate probability of assignments A or B being correct given the CP3 values
    p_A_given_cp3 = p_cp3_given_A / (p_cp3_given_A + p_cp3_given_B)
    p_B_given_cp3 = p_cp3_given_B / (p_cp3_given_A + p_cp3_given_B)

    #TODO: Add 13C and 1H analysis

    # print formatted output
    print("ASSIGNMENT A: ({}, {}) -> ({}, {})".format(expt_a.name, expt_b.name, calc_a.name, calc_b.name))
    print("ASSIGNMENT B: ({}, {}) -> ({}, {})".format(expt_b.name, expt_a.name, calc_a.name, calc_b.name))
    print()

    print("-------------------      -------------------      -------------------")
    print("Combined 13C and 1H      13C only                 1H only")
    print("-------------------      -------------------      -------------------")
    print("CP3(A)  : {:9.6f}      CP3(A)  : {:9.6f}      CP3(A)  : {:9.6f}".format(cp3_A, cp3_A, cp3_A))
    print("P(CP3|A): {:9.6f}      P(CP3|A): {:9.6f}      P(CP3|A): {:9.6f}".format(p_cp3_given_A, p_cp3_given_A, p_cp3_given_A))
    print("CP3(B)  : {:9.6f}      CP3(B)  : {:9.6f}      CP3(B)  : {:9.6f}".format(cp3_B, cp3_B, cp3_B))
    print("P(CP3|B): {:9.6f}      P(CP3|B): {:9.6f}      P(CP3|B): {:9.6f}".format(p_cp3_given_B, p_cp3_given_B, p_cp3_given_B))
    print()
    print("P(A|CP3): {:9.6f}      P(A|CP3): {:9.6f}      P(A|CP3): {:9.6f}".format(p_A_given_cp3, p_A_given_cp3, p_A_given_cp3))
    print("P(B|CP3): {:9.6f}      P(B|CP3): {:9.6f}      P(B|CP3): {:9.6f}".format(p_B_given_cp3, p_B_given_cp3, p_B_given_cp3))

    return 0


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
                # Runs CP3 analysis for all pairs of columns in calculated/experimental data
                cp3(calc_df['atom'], calc_df.iloc[:, i + 2], calc_df.iloc[:, j + 2],
                    expt_df.iloc[:, i + 2], expt_df.iloc[:, j + 2])

    print()
    print("Please cite: Smith, S. G.; Goodman, J. M. J. Org. Chem. 2009, 74 (12), 4597–4607.")

