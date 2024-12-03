#!/usr/bin/env python3

from pymatgen.io.vasp.outputs import Eigenval
band_gap, cbm, vbm, is_band_gap_direct = Eigenval("EIGENVAL").eigenvalue_band_properties

print(f"band_gap: {band_gap} eV")
print(f"cbm: {cbm} eV")
print(f"vbm: {vbm} eV")
print(f"is_band_gap_direct: {is_band_gap_direct}")