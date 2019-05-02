#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("earlier_csv",
                        action='store',
                        help='.csv file from an earlier step (before filtering).')
    parser.add_argument("later_csv",
                        action='store',
                        help='.csv file from a later step (after filtering).')
    parser.add_argument('-t',
                        '--threshold',
                        type=float,
                        action='store',
                        help='Energy cutoff (in kcal/mol) for the next round of filtering. '
                             'For more explanation see the README.')
    parser.add_argument('-d',
                        "--diagonal",
                        action="store_true",
                        help="Plots a y = x line.")
    return parser.parse_args()


def get_energies(file):
    conformer_energies = []
    with open(file, 'r') as csv_file:
        for line in csv_file:
            if not line.lstrip().startswith(","):
                conformer_energies.append(float(line.rstrip("\n").split(",")[-1]))
    return conformer_energies


if __name__ == '__main__':
    args = get_args()

    # Extracts energies from CSV files and stores them in numpy arrays
    earlier_energies = np.array(get_energies(args.earlier_csv))
    later_energies = np.array(get_energies(args.later_csv))

    # sets zero of energy to be the lowest-energy conformers
    earlier_energies = earlier_energies - np.amin(earlier_energies)
    later_energies = later_energies - np.amin(later_energies)

    fig, ax = plt.subplots()

    # visually distinguish conformers below/above the threshold
    if args.threshold:
        earlier_energies_pass = earlier_energies[later_energies <= args.threshold]
        later_energies_pass = later_energies[later_energies <= args.threshold]
        earlier_energies_fail = earlier_energies[later_energies > args.threshold]
        later_energies_fail = later_energies[later_energies > args.threshold]

        ax.scatter(earlier_energies_pass, later_energies_pass, s=12, color='green')
        ax.scatter(earlier_energies_fail, later_energies_fail, s=4, color='red')
        ax.plot([0, np.amax(earlier_energies)], [args.threshold, args.threshold], linewidth=0.9)
    else:
        ax.scatter(earlier_energies, later_energies, s=10)

    # plots the line y = x if requested
    if args.diagonal:
        ax.plot([0, max(np.amax(earlier_energies), np.amax(later_energies))], [0, max(np.amax(earlier_energies), np.amax(later_energies))], linewidth=0.9,  color='orange')

    plt.xlabel(args.earlier_csv.replace(".csv", "") + " energy (kcal/mol)")
    plt.ylabel(args.later_csv.replace(".csv", "") + " energy (kcal/mol)")
    plt.show()
