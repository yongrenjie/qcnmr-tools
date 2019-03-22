#!/usr/bin/env python3

import sys
import pandas as pd


def cp3(atoms, calc_a, calc_b, expt_a, expt_b):
    print()
    print(atoms.name, calc_a.name, calc_b.name, expt_a.name, expt_b.name)
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
    print("Calculated data")
    print("===============")
    print(calc_df)
    print()
    print("=================")
    print("Experimental data")
    print("=================")
    print(expt_df)


    number_of_isomers = len(calc_df.columns) - 2   # 2

    for i in range(number_of_isomers): # 0, 1
        for j in range(number_of_isomers):
            if j <= i:
                pass
            else:
                cp3(calc_df['atom'], calc_df.iloc[:, i+2], calc_df.iloc[:, j+2], expt_df.iloc[:, i+2], expt_df.iloc[:, j+2])