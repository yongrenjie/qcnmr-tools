#!/usr/bin/env python3

# This script (hopefully) scans a set of .xyz files, then removes methanol molecule(s) from each file to make each file
# have the same number of methanol molecules.
# It does this by calculating the distance from the MeOH oxygen to every atom of the solute. The minimum distance in
# this set is considered to be the MeOH–solute distance. The script then removes the MeOH molecules which are (by this
# definition) furthest away from the solute.

import argparse
import math
import os


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", action='store', help='.xyz file(s) to analyse', nargs="*")
    return parser.parse_args()


def get_n_atoms(xyz_file):
    # This assumes that the header line of the xyz file has the number of atoms. Apparently this isn't compulsory,
    # but I don't care. If you have non-standard xyz files it's on you to make a script yourself...
    with open(xyz_file, "r") as xyz:
        n_atoms = int(xyz.readline().strip())
    return n_atoms


def calculate_meoh_solute_distance(solute_coord, meoh_o_coord):
    # solute_coord should be a list of lists containing the x,y,z coordinates of each atom of the solute
    # meoh_o_coord is just one list
    smallest_distance = 100000000       # ridiculously large number
    for atom_coord in solute_coord:
        meoh_o_atom_distance = math.sqrt((meoh_o_coord[0] - atom_coord[0])**2
                                         + (meoh_o_coord[1] - atom_coord[1])**2
                                         + (meoh_o_coord[2] - atom_coord[2])**2)
        if meoh_o_atom_distance < smallest_distance:
            smallest_distance = meoh_o_atom_distance
    return smallest_distance


def strip_meoh(xyz_file, n_atoms_desired):
    # n_atoms_desired is the number of atoms to strip down to
    n_atoms_original = get_n_atoms(xyz_file)
    n_meoh_to_strip = int((n_atoms_original - n_atoms_desired) / 6)

    os.system("mkdir -p stripped_conformers")

    # skip all of it if we don't need to remove anything
    if n_meoh_to_strip == 0:
        print("Not touching {}!".format(file))
        os.system("cp {} {}".format(xyz_file, "stripped_conformers/stripped_" + xyz_file))
        return 0

    print("Stripping {} methanol molecules from {}...".format(n_meoh_to_strip, xyz_file), end="")

    n_solute_atoms = 36     # hardcoded for Kishi triols

    # get a list of methanol–solute distances
    with open(xyz_file, "r") as xyz:
        solute_coord = []
        meoh_distances = []
        for line_number, line in enumerate(xyz):
            if 2 <= line_number < n_solute_atoms + 2:       # line_number between 2 and 37 are coordinates of solute
                solute_coord.append([float(i) for i in line.split()[1:]])       # wow, I'm learning list comprehension
            elif line_number >= n_solute_atoms + 2 and line.split()[0] == "O":  # lines corresponding to MeOH oxygen
                # by the time any of this code gets executed, solute_coord should be fully built up already
                meoh_o_coord = [float(i) for i in line.split()[1:]]
                meoh_distances.append(calculate_meoh_solute_distance(solute_coord, meoh_o_coord))

    # find the n_meoh_to_strip furthest methanols
    meoh_distances_to_remove = sorted(meoh_distances)[-n_meoh_to_strip:]

    # print the output file
    output_file_name = "stripped_conformers/stripped_" + xyz_file
    with open(output_file_name, "w") as out_xyz_file:

        # print the two header lines and the solute coordinates
        with open(xyz_file, "r") as xyz:
            print(n_atoms_desired, file=out_xyz_file)
            for line_number, line in enumerate(xyz):
                if 1 <= line_number < n_solute_atoms + 2:
                    print(line.rstrip(), file=out_xyz_file)
                if line_number > n_solute_atoms + 2:
                    break           # skips iterating over the rest of the file

        # print the MeOH coordinates, but only if the distance is not inside meoh_distances_to_remove
        with open(xyz_file, "r") as xyz:
            for line_number, line in enumerate(xyz):
                if line_number >= n_solute_atoms + 2:
                    meoh_number = ((line_number - n_solute_atoms - 2) // 6)
                    # line_number between 38 and 43 = MeOH number 0, etc.
                    if meoh_distances[meoh_number] not in meoh_distances_to_remove:
                        print(line.rstrip(), file=out_xyz_file)
        print(" ...done!")

    return 0


if __name__ == '__main__':
    args = get_args()

    # find the smallest xyz file, i.e. figure out how short it should trim each xyz file to
    smallest_number_of_atoms = 100000000000  # ridiculously large number
    for file in args.filenames:
        number_of_atoms = get_n_atoms(file)
        if number_of_atoms < smallest_number_of_atoms:
            smallest_number_of_atoms = number_of_atoms
    print("There are {} files in total.".format(len(args.filenames)))
    print("The smallest file has {} atoms.".format(smallest_number_of_atoms))

    # strip MeOH molecules
    for file in args.filenames:
        strip_meoh(file, smallest_number_of_atoms)
    print()
    print("Please run 'wc -l *.xyz' in the new directory to check that all the files have the same length.")
    print("They should all have {} lines.".format(smallest_number_of_atoms + 2))
    print()

