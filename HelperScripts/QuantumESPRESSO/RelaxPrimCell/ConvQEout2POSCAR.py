#!/usr/bin/env python3

import os
import glob
import shutil
from pymatgen.core.structure import Structure
from pymatgen.io.vasp.inputs import Poscar

def FindAndReplace(fileName, strToFind, strToReplace):
    strToFind = str(strToFind)
    strToReplace = str(strToReplace)
    with open(fileName, "r") as file:
            fileData = file.read()

    fileData = fileData.replace(strToFind, strToReplace)
    with open(fileName, "w") as file:
            file.write(str(fileData))

def ConvCifToPOSCAR():
    cifFile=glob.glob("*.cif")[0]
    struct=Structure.from_file(cifFile)
    Poscar(struct).write_file("POSCAR", significant_figures=16)

os.system("ConvQEout2Cif.py")
ConvCifToPOSCAR()
