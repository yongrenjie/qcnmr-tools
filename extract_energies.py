import argparse
import matplotlib.pyplot as plt
import pandas as pd

HARTREE_TO_KCAL = 627.509

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filename", action='store', help='.out file to analyse')
    parser.add_argument("-t", "--threshold", type=int, default=0, help="Specify threshold energy (kcal/mol)")
    parser.add_argument("-p", "--plot", action='store_true', help='Plot energies of all conformers')
    parser.add_argument("-c", "--csv", action='store_true', help='Output all conformers to csv file')
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()
    threshold_kcal = args.threshold
    sp_outputfile = args.filename

    # determine what output file we are reading (CREST or ORCA)
    output_file_determined = False
    output_file_type = ""
    while not output_file_determined:
        with open(sp_outputfile, 'r') as outputfile:
            for line in outputfile:
                if "C R E S T" in line:
                    output_file_type = "crest"
                    output_file_determined = True
                    break
                elif "O R C A" in line:
                    output_file_type = "orca"
                    output_file_determined = True
                    break

    conformer_numbers = []
    conformer_energies = []

    if output_file_type == "crest":
        energy_block = False
        with open(sp_outputfile, 'r') as outputfile:
            for line in outputfile:
                if line.strip().startswith("number of unique conformers for further calc"):
                    energy_block = True
                if line.strip().startswith("NMR mode"):
                    energy_block = False
                if energy_block:
                    if line.split()[0].isdigit():
                        conformer_numbers.append(int(line.split()[0]))
                        conformer_energies.append(float(line.split()[1]))
        all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})

    elif output_file_type == "orca":
        with open(sp_outputfile, 'r') as outputfile:
            for line in outputfile:
                if line.strip().startswith("MULTIPLE XYZ STEP"):
                    conformer_numbers.append(int(line.split()[-1]))
                if line.strip().startswith("FINAL SINGLE POINT ENERGY"):
                    conformer_energies.append(float(line.split()[-1]))

        all_conformers = pd.DataFrame({'num': conformer_numbers, 'energy': conformer_energies})
        all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL

    # all_conformers['energy'] = (all_conformers['energy'] - all_conformers['energy'].min()) * HARTREE_TO_KCAL
    # Not needed for CREST output, already in kcal/mol
    print(all_conformers)

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

        csv_filename = sp_outputfile.rstrip(".out") + "_filtered.csv"
        filtered_conformers.to_csv(csv_filename, columns=['num','energy'])
        print("Conformers within {} kcal/mol written to {}.".format(threshold_kcal, csv_filename))

    if args.csv:
        csv_filename = sp_outputfile.replace(".out", ".csv")
        all_conformers.to_csv(csv_filename, columns=['num','energy'])
        print("All conformers written to {}.".format(csv_filename))
