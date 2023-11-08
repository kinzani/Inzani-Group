#!/usr/bin/env python3

import argparse
from pymatgen.ext.matproj import MPRester
from pymatgen.io.vasp.inputs import Poscar

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--mpid", type=str, help="Materials Project ID")
args = parser.parse_args()


APIkey = "1TmQ7TKwpVLOiv8Z"

print("Getting structure.")

with MPRester(APIkey) as mpr:
    try:
        struct = mpr.get_structure_by_material_id(args.mpid)
        print("Structure successfully acquired.")
        print(f"Writing POSCAR file for {args.mpid}")
        Poscar(struct).write_file("POSCAR", significant_figures=16)

        #POSCARs from the Materials Project have the first line as the formula of the material with spaces in-between the atoms
        with open("POSCAR", mode="r") as file:
            formula = file.readline()
            formula = formula.replace(" ", "").strip() #need to remove all spaces. .strip() is necessary otherwise some weird hidden character is at the end of the file name below

        print(f"POSCAR file written for {args.mpid}.")
        print(f"Material formula is: {formula}")

    except:
        print("Input was not a valid Materials Project ID.")
