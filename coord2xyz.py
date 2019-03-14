#!/usr/bin/env python3

import argparse

BOHR_TO_ANG = 0.52917721067   # from https://physics.nist.gov/cgi-bin/cuu/Value?bohrrada0


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames", action='store', help='.coord file(s) to convert to xyz', nargs="*")
    return parser.parse_args()


def coord_to_xyz(coord_filename):
    with open(coord_filename, "r") as file:

        coord_coordinates = []
        coordinate_block = False

        for line in file:
            if "$end" in line:
                coordinate_block = False  # signal end of atomic coordinates
            if coordinate_block:
                coord_coordinates.append(line)  # get coordinate lines into a list
            if "$coord" in line:
                coordinate_block = True  # signal start of atomic coordinates

    # convert lines in coord to correct format for xyz file
    xyz_coordinates = []
    for line in coord_coordinates:
        [x_bohr, y_bohr, z_bohr, atom] = line.split()
        x_ang = float(x_bohr) * BOHR_TO_ANG
        y_ang = float(y_bohr) * BOHR_TO_ANG
        z_ang = float(z_bohr) * BOHR_TO_ANG
        xyz_coordinates.append("{} {:11.7f} {:11.7f} {:11.7f}".format(atom, x_ang, y_ang, z_ang))

    # print everything to the xyz file
    base_name = coord_filename.rstrip(".coord").rstrip("coord")
    xyz_file = base_name + ".xyz"
    with open(xyz_file, "w") as output_file:
        print(len(xyz_coordinates), file=output_file) # number of atoms
        print(base_name, file=output_file) # comment line in xyz file format
        for line in xyz_coordinates:
            print(line, file=output_file)
    return 0



if __name__ == "__main__":
    args = get_args()
    for file in args.filenames:
        coord_to_xyz(file)
