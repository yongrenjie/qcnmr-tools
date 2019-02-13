import matplotlib.pyplot as plt
import os
import sys


def determine_output_file():
    output_file = ''
    if len(sys.argv) == 2:
        output_file = sys.argv[1]
    else:
        for file in os.listdir(os.getcwd()):
            if file.endswith('.anmr.dat') and not file.startswith('.'):
                output_file = file
    return output_file


def determine_title():
    title = ''
    for file in os.listdir(os.getcwd()):
        if (file.endswith('.inp') and not file.endswith('anmr.inp')
                and not file.endswith('confscript.inp') and not file.startswith('.')):
            title = file.rstrip('.inp')
    return title


def main():
    x = []
    y = []
    output_file = determine_output_file()
    title = determine_title()
    if os.path.isfile(output_file):  # Check if file exists
        print("Plotting spectrum of '{}' from {}...".format(title, output_file))
        with open(output_file, 'r') as file:
            for line in file:
                a, b = line.split()
                x.append(-float(a))
                y.append(float(b))

        plt.plot(x, y, label='NMR spectrum')
        plt.xlabel('Chemical shift / ppm')
        plt.ylabel('Intensity / a.u.')
        plt.xlim(plt.xlim()[::-1])
        plt.title(title)
        plt.show()
    else:
        if len(sys.argv) == 2:
            print("The file '{}' was not found.".format(sys.argv[1]))
        else:
            print("An .anmr.dat file was not found.")
        print("You can pass the file name as a command line argument, e.g.")
        print("$ python3 anmr_plot.py SPECTRUM.anmr.dat")


main()
