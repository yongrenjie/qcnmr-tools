#!/usr/bin/env python3

import os


def conv(file_name):
    converged = False
    with open(file_name, "r") as file:
        for line in file:
            if "THE OPTIMIZATION HAS CONVERGED" in line:
                converged = True
    return converged


if __name__ == "__main__":
    not_converged = [i for i in os.listdir() if i.endswith(".out") and not conv(i)]
    print("Files not converged:")
    print("\n".join(not_converged))
    print(len(not_converged))
