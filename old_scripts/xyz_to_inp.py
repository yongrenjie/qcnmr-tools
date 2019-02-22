#!/usr/bin/env python3

import argparse

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("filenames",
                        action='store',
                        help='.xyz files to convert into input files.',
                        nargs="*")
    parser.add_argument("-s",
                        "--shielding",
                        action="store_true",
                        help="Print eprnmr block at the end of the file for shielding calculations")
    parser.add_argument("-j",
                        "--hhcoupling",
                        action="store_true",
                        help="Print eprnmr block at the end of the file for 1H-1H coupling calculations")
    parser.add_argument("-c",
                        "--chcoupling",
                        action="store_true",
                        help="Print eprnmr block at the end of the file for 13C-1H coupling calculations")
    return parser.parse_args()

if __name__ == '__main__':
    args = get_args()

    if args.shielding + args.hhcoupling + args.chcoupling > 1:
        print("Don't ask for more than one thing at once!")
        print("Defaulting to printing shielding block...")
        args.shielding = True
        args.hhcoupling = False
        args.chcoupling = False

    keywords = "! PBE0 cc-pVTZ cc-pVTZ/JK D3BJ CPCM(Methanol) PAL4"
    eprnmr_shielding = "%eprnmr\n" \
                        "    Ori = GIAO\n" \
                        "    Nuclei = all C { shift }\n" \
                        "    Nuclei = all H { shift }\n" \
                        "end"
    eprnmr_coupling_hh =  "%eprnmr\n" \
                        "    Ori = GIAO\n" \
                        "    Nuclei = all H { ssfc, ist = 1 }\n" \
                        "    SpinSpinRThresh 6.0\n" \
                        "end"
    eprnmr_coupling_ch = "%eprnmr\n" \
                         "    Ori = GIAO\n" \
                         "    Nuclei = all H { ssall, ist = 1 }\n" \
                         "    SpinSpinRThresh 1.3\n" \
                         "end"

    for file in args.filenames:
        conformer_number = int(file.split(".")[-2].split("_")[1])  # gets conformer number from file name
        if args.shielding:
            inp_name = base_inp_name.replace("opt", "nmr_s")
        elif args.hhcoupling:
            inp_name = base_inp_name.replace("opt", "nmr_c_hh")
        elif args.chcoupling:
            inp_name = base_inp_name.replace("opt", "nmr_c_ch")

        with open(file, 'r') as xyz_file:
            line_count = 1
            with open(inp_name, 'w') as inp_file:
                print(keywords, file=inp_file)
                print("", file=inp_file)
                print("*xyz 0 1", file=inp_file)
                for line in xyz_file:
                    if line_count >= 3:
                        print(line.rstrip("\n"), file=inp_file)
                    line_count = line_count + 1
                print("*", file=inp_file)
                print("", file=inp_file)
                if args.shielding:
                    print(eprnmr_shielding, file=inp_file)
                elif args.hhcoupling:
                    print(eprnmr_coupling_hh, file=inp_file)
                elif args.chcoupling:
                    print(eprnmr_coupling_ch, file=inp_file)
                print("", file=inp_file)