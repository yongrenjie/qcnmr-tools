#!/usr/bin/env python3

import os
import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--filename", help='File containing clustered conformers (default clusters_try.pdb)',
                        default="clusters_try.pdb")
    parser.add_argument("--minsize", help="Minimum size of cluster (i.e. number of conformations in cluster) to output an xyz file for", type=int, default=1)
    parser.add_argument("--explicit", action="store_true", help="Save xyz files including MeOH within 3.5 Ang of lig")
    return parser.parse_args()


def count_clusters(log_file, threshold):
    # from the cluster.log file, determines how many clusters have more than <threshold> conformations
    # if threshold = 0, this simply returns the total number of clusters
    with open(log_file, "r") as file:
        for line in file:
            if len(line.split()) >= 3:
                if line.split()[0].isdigit() and int(line.split()[2]) > threshold:
                    total_clusters_above_threshold = int(line.split()[0])
    return total_clusters_above_threshold


def add_zeroes(j):
    # turns 9 -> 0009, 192 -> 0192, etc.
    jstr = ""
    for c in range(4 - len(str(j))):
        jstr = jstr + "0"
    jstr = jstr + str(j)
    return jstr


if __name__ == "__main__":
    args = get_args()
    
    # could implement some smart searching here
    clust_file = args.filename
    
    # could implement some smart searching here too
    log_file = "cluster.log"
    clusters_to_print = count_clusters(log_file, args.minsize)
    
    # updates selection algebra for PyMol if explicit solvent is needed/desired
    selection_algebra = ""
    if args.explicit:
        selection_algebra = " and byres all within 3.5 of resn jl1"
    
    # creates PyMol script which actually does the tough work
    with open("pymol.pml", "w") as pymol_s:
        print("load {}, clust".format(clust_file), file=pymol_s)
        print("split_states clust", file=pymol_s)
        for i in range(1, clusters_to_print + 1):
            print("save conf_{}.xyz, clust_{}{}".format(i, add_zeroes(i), selection_algebra), file=pymol_s)
        print("quit", file=pymol_s)
    
    # runs PyMol script from command line and cleans up the folder
    os.system("pymol -c pymol.pml")
    os.system("rm pymol.pml")
    os.system("mkdir -p conformers")
    os.system("mv *.xyz conformers")