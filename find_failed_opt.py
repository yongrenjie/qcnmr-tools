#!/usr/bin/env python3

import os


if __name__ == "__main__":

    grep = os.popen("grep -i 'HURRAY' *.out").read()
    converged = [i.split()[0][:-1] for i in grep.split("\n") if len(i.split()) > 1]

    ls = os.popen("ls *.out").read()
    all_out_files = ls.split()

    not_converged = [j for j in all_out_files if not j in converged]

    print()
    print("{} file(s) in this directory not converged".format(len(not_converged)))
    print("\n".join(not_converged))

