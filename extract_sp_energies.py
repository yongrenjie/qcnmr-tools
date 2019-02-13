import sys
import matplotlib.pyplot as plt
import numpy as np

HARTREE_TO_KCAL = 627.509

def main():
    conformer_numbers = np.array([])
    conformer_energies = np.array([])
    sp_outputfile = sys.argv[1]
    with open(sp_outputfile, 'r') as outputfile:
        for line in outputfile:
            if line.strip().startswith("MULTIPLE XYZ STEP"):
                conformer_numbers = np.append(conformer_numbers, int(line.split()[-1]))
            if line.strip().startswith("FINAL SINGLE POINT ENERGY"):
                conformer_energies = np.append(conformer_energies, float(line.split()[-1]))
    conformer_energies = (conformer_energies - np.amin(conformer_energies)) * HARTREE_TO_KCAL
    plt.plot(conformer_numbers,conformer_energies)
    plt.xlabel("conformer number")
    plt.ylabel("energy kcal/mol")
    plt.show()
    threshold_kcal = 3
    print("out of {} conformers {} are < {} kcal/mol from lowest energy".format(conformer_numbers[-1], len(np.where(conformer_energies < threshold_kcal)[0]), threshold_kcal))
    return 0

main()
