#!/usr/bin/env python3

import matplotlib.pyplot as plt
import argparse


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("outfile", action='store', help='.out file to analyse')
    return parser.parse_args()


if __name__ == '__main__':
    args = get_args()
    with open(args.outfile, "r") as out_file:
        x = []
        y = []
        results = False
        for line in out_file:
            if "The Calculated Surface using the 'Actual Energy'" in line:
                results = True
            if len(line.split()) == 0:
                results = False
            if results:
                if len(line.split()) == 2:
                    x.append(float(line.split()[0]))
                    y.append(float(line.split()[1]))

plt.plot(x,y)
plt.show()
