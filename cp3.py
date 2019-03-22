#!/usr/bin/env python3

import pandas as pd
import math

CORRECT_MEAN = [0.512, 0.547, 0.478]            # [Combined, 13C, 1H]
CORRECT_SD = [0.209, 0.253, 0.305]
INCORRECT_MEAN = [-0.637, -0.487, -0.786]
INCORRECT_SD = [0.499, 0.533, 0.835]


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
    cp3_A = [0, 0, 0]
    cp3_B = [0, 0, 0]
    p_cp3_given_A = [0, 0, 0]
    p_cp3_given_B = [0, 0, 0]
    p_A_given_cp3 = [0, 0, 0]
    p_B_given_cp3 = [0, 0, 0]

    c13_logical_array = pd.Series(atoms == 'C')
    h1_logical_array = pd.Series(atoms == 'H')

    # calculate CP3 for assignment A (first calc column = first expt column)
    cp3_A[0] = calculate_cp3_value(calc_a, calc_b, expt_a, expt_b)
    cp3_A[1] = calculate_cp3_value(calc_a * c13_logical_array, calc_b * c13_logical_array,
                                   expt_a * c13_logical_array, expt_b * c13_logical_array)
    cp3_A[2] = calculate_cp3_value(calc_a * h1_logical_array, calc_b * h1_logical_array,
                                   expt_a * h1_logical_array, expt_b * h1_logical_array)
    # calculate CP3 for assignment B (first calc column = second expt column)
    cp3_B[0] = calculate_cp3_value(calc_a, calc_b, expt_b, expt_a)
    cp3_B[1] = calculate_cp3_value(calc_a * c13_logical_array, calc_b * c13_logical_array,
                                   expt_b * c13_logical_array, expt_a * c13_logical_array)
    cp3_B[2] = calculate_cp3_value(calc_a * h1_logical_array, calc_b * h1_logical_array,
                                   expt_b * h1_logical_array, expt_a * h1_logical_array)

    print()
    print("==================================================")
    print()
    for i in range(3): # i = 0: combined; i = 1: 13C; i = 2: 1H
        # calculate probability of obtaining CP3 values given that assignment A is correct
        p_cp3_given_A[i] = min(normal_cdf(cp3_A[i], CORRECT_MEAN[i], CORRECT_SD[i]),
                               1 - normal_cdf(cp3_A[i], CORRECT_MEAN[i], CORRECT_SD[i])) * \
                           min(normal_cdf(cp3_B[i], INCORRECT_MEAN[i], INCORRECT_SD[i]),
                               1 - normal_cdf(cp3_B[i], INCORRECT_MEAN[i], INCORRECT_SD[i])) * 4
        # calculate probability of obtaining CP3 values given that assignment B is correct
        p_cp3_given_B[i] = min(normal_cdf(cp3_A[i], INCORRECT_MEAN[i], INCORRECT_SD[i]),
                               1 - normal_cdf(cp3_A[i], INCORRECT_MEAN[i], INCORRECT_SD[i])) * \
                           min(normal_cdf(cp3_B[i], CORRECT_MEAN[i], CORRECT_SD[i]),
                               1 - normal_cdf(cp3_B[i], CORRECT_MEAN[i], CORRECT_SD[i])) * 4
        # calculate probability of assignments A or B being correct given the CP3 values
        p_A_given_cp3[i] = p_cp3_given_A[i] / (p_cp3_given_A[i] + p_cp3_given_B[i])
        p_B_given_cp3[i] = p_cp3_given_B[i] / (p_cp3_given_A[i] + p_cp3_given_B[i])

    # print formatted output
    print("ASSIGNMENT A: ({}, {}) -> ({}, {})".format(expt_a.name, expt_b.name, calc_a.name, calc_b.name))
    print("ASSIGNMENT B: ({}, {}) -> ({}, {})".format(expt_b.name, expt_a.name, calc_a.name, calc_b.name))
    print()

    print("-------------------      -------------------      -------------------")
    print("Combined 13C and 1H      13C only                 1H only")
    print("-------------------      -------------------      -------------------")
    print("CP3(A)  : {:9.6f}      CP3(A)  : {:9.6f}      CP3(A)  : {:9.6f}".format(cp3_A[0],
                                                                                   cp3_A[1],
                                                                                   cp3_A[2]))
    print("CP3(B)  : {:9.6f}      CP3(B)  : {:9.6f}      CP3(B)  : {:9.6f}".format(cp3_B[0],
                                                                                   cp3_B[1],
                                                                                   cp3_B[2]))
    print()
    print("P(CP3|A): {:9.6f}      P(CP3|A): {:9.6f}      P(CP3|A): {:9.6f}".format(p_cp3_given_A[0],
                                                                                   p_cp3_given_A[1],
                                                                                   p_cp3_given_A[2]))
    print("P(CP3|B): {:9.6f}      P(CP3|B): {:9.6f}      P(CP3|B): {:9.6f}".format(p_cp3_given_B[0],
                                                                                   p_cp3_given_B[1],
                                                                                   p_cp3_given_B[2]))
    print()
    print("P(A|CP3): {:9.6f}      P(A|CP3): {:9.6f}      P(A|CP3): {:9.6f}".format(p_A_given_cp3[0],
                                                                                   p_A_given_cp3[1],
                                                                                   p_A_given_cp3[2]))
    print("P(B|CP3): {:9.6f}      P(B|CP3): {:9.6f}      P(B|CP3): {:9.6f}".format(p_B_given_cp3[0],
                                                                                   p_B_given_cp3[1],
                                                                                   p_B_given_cp3[2]))

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

    number_of_isomers = len(calc_df.columns) - 2

    for m in range(number_of_isomers):
        for n in range(number_of_isomers):
            if n > m:
                # Runs CP3 analysis for all pairs of columns in calculated/experimental data
                cp3(calc_df['atom'], calc_df.iloc[:, m + 2], calc_df.iloc[:, n + 2],
                    expt_df.iloc[:, m + 2], expt_df.iloc[:, n + 2])

    print()
    print("==================================================")
    print()
    print("Please cite: Smith, S. G.; Goodman, J. M. J. Org. Chem. 2009, 74 (12), 4597–4607.")

