#!/usr/bin/env python3

import argparse
from pymatgen.core.structure import Structure
from scipy.spatial.transform import Rotation as R
import numpy as np
import numpy as np
from pymatgen.io.cif import CifWriter
from pymatgen.io.vasp import Poscar

parser = argparse.ArgumentParser(
                                prog='RotateAtoms',
                                description='This program takes a structure file, a list of atom indices (0-indexed), the x and y fractional coords of an axis of rotation (aligned with the z-axis) and an angle of rotation in degrees, and rotates the selected atoms around that axis and returns a rotated .cif file.',
                                epilog='Hope this helps!'
                                )

parser.add_argument("-f", '--file', type=str, default="POSCAR", help="Filepath to structure file.")
parser.add_argument("-i", '--indices', action='store', type=int, nargs="+", help="List of atom indices (0-indexed) separated by spaces.")
parser.add_argument("-p", '--point', action='store', type=float, nargs=2, help="x and y fractional coordinates of the axis of rotation. Coordinates must be passed in separated by spaces")
parser.add_argument("-a", '--angle', type=float, help="Angle of rotation in degrees.")
parser.add_argument("-o", '--outputType', type=str, default="cif", help="Output file type - POSCAR or cif. .cif is the default file type.")

args = parser.parse_args()

struct_file = args.file
atom_indices = args.indices
x_and_y_forAxis = args.point
angle_of_rot = args.angle
output_file_type = args.outputType.lower()

file_prefix = struct_file.split(".")[0]
struct = Structure.from_file(struct_file)
atom_frac_coords = [struct[i].frac_coords for i in atom_indices]

r = R.from_euler('z', angle_of_rot, degrees=True)
rotvec_point = [*x_and_y_forAxis, 0.]
soa = np.array([[*rotvec_point, *[0,0,1.]]])
relative_coords = [np.array(point) - np.array(rotvec_point) for point in atom_frac_coords]
rotated_relative_coords = [r.as_matrix() @ np.array(relative_point) for relative_point in relative_coords]
rotated_coords = np.array([np.array(rotated_relative_point) + np.array(rotvec_point) for rotated_relative_point in rotated_relative_coords])

for i, coord in zip(atom_indices, rotated_coords):
    struct[i].frac_coords = coord

if(output_file_type == "cif"):
    CifWriter(struct).write_file(f"rotated_{file_prefix}.cif")
    print(f"rotated_{file_prefix}.cif created.")
elif(output_file_type == "poscar"):
    Poscar(struct).write_file(f"rotated_{file_prefix}_POSCAR.vasp")
    print(f"rotated_{file_prefix}_POSCAR.vasp created.")
else:
    print(f"File type {output_file_type} not recognised. You need to specify cif or poscar.")