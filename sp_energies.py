import argparse
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

HARTREE_TO_KCAL = 627.509

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", action='store', help='.out file to analyse')
    parser.add_argument("-t", "--threshold", type=int, default=0, help="Specify threshold energy (kcal/mol) (default = 3)")
    parser.add_argument("-p", "--plot", action='store_true', help='Plot energies of all conformers')
    parser.add_argument("-c", "--csv", action='store_true', help='Output sorted conformers to csv file')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    threshold_kcal = args.threshold
    sp_outputfile = args.filename
    conformer_numbers = []
    conformer_energies = []
    with open(sp_outputfile, 'r') as outputfile:
        for line in outputfile:
            if line.strip().startswith("MULTIPLE XYZ STEP"):
                conformer_numbers.append(int(line.split()[-1]))
            if line.strip().startswith("FINAL SINGLE POINT ENERGY"):
                conformer_energies.append(float(line.split()[-1]))

    all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})
    all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL

    if args.plot:
        all_conformers.plot(x='num', y='energy', kind='line')
        plt.xlabel("Conformer number")
        plt.ylabel("Energy (kcal/mol relative to lowest)")
        plt.show()

    if args.threshold > 0:
        threshold_kcal = args.threshold
        filtered_conformers = all_conformers[all_conformers['energy'] <= threshold_kcal]
        filtered_conformers = filtered_conformers.sort_values('energy')
        filtered_conformers = filtered_conformers.reset_index(drop=True)
        print(filtered_conformers)

    if args.csv:
        csv_filename = sp_outputfile.replace(".out", ".csv")
        all_conformers.to_csv(csv_filename, columns=['num','energy'])