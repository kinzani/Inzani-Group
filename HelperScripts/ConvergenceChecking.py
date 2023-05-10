#!/usr/bin/env python3

from pymatgen.io.vasp.outputs import Vasprun
import warnings
warnings.filterwarnings("ignore") #so, funny story, for whatever reason this script will just scream at you for no apparent reason for import the Vasprun class, despite it being incredibly useful and widely used. This wasn't always the case, but it is now, so I've just hidden warnings for this script lol.

def ConvergenceChecking():
    vasprunObj = Vasprun("vasprun.xml")
    return vasprunObj.converged

truth=ConvergenceChecking()
print(truth)
