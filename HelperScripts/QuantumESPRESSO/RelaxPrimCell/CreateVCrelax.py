#!/usr/bin/env python3

from ase.io import read, write
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


cifFile=glob.glob("*.cif")[0]
qeOutputFilePrefix=cifFile.replace(".out", "")
prefix = cifFile.replace(".cif", "")

relaxDirs=glob.glob("Step*")
print(relaxDirs)
lastCalcNum=int([step.replace("Step", "") for step in relaxDirs][-1])
os.chdir(f"Step{lastCalcNum}")
os.system("../ConvQEout2POSCAR.py")
os.system("ConvPOSCAR2cif.py")
os.chdir("..")
calcNum=lastCalcNum+1
os.mkdir(f"Step{calcNum}")
shutil.copy("ExecuteAndWait", f"Step{calcNum}")
shutil.copy(f"Step{lastCalcNum}/{cifFile}", f"Step{calcNum}")
os.chdir(f"Step{calcNum}")

struct=read(cifFile)
elements=list(set(struct.symbols))
pseudo_dir = '/home/d/dcriveanu/DFTplusU/YAG/QuantumEspresso/pseudos_YAGCe'
pseudos = glob.glob(f"{pseudo_dir}/*")
pseudos = [pp.replace(f"{pseudo_dir}/", "") for pp in pseudos]
pseudopotentials = []
for elem in elements:
    for pp in pseudos:
        if pp.startswith(f"{elem}."):
            pseudopotentials.append(pp)
atomic_species = dict(zip(elements, pseudopotentials))
ecutwfc = 81
kpts = [2,2,2]

control = {'title': prefix,
           'calculation': "relax",
           'verbosity': 'high',
           'restart_mode': 'from_scratch',
           "forc_conv_thr": 3.889e-05,
           'prefix': prefix,
           'outdir': "./" ,
           'nstep': 400,
           'pseudo_dir': str(pseudo_dir)}
system = {'ecutwfc': ecutwfc,
        'occupations': 'smearing',
        'degauss': 3e-3}
electrons = {'diagonalization':'david',
             'conv_thr': 7.350e-09,
             'electron_maxstep': 200,
             'startingpot': 'atomic',
             'startingwfc': 'atomic',
             'mixing_mode': 'plain',
             'mixing_beta': 0.2,
             'mixing_ndim': 10}
ions = {"ion_dynamics": 'bfgs'}



cell={"cell_dofree": 'all'} #it seems to be recommended for me to add in this CELL card when doing vc-relax calcs.
control.update({'calculation': 'vc-relax'}) #now using variable cell relaxations
struct.write(f"{prefix}.in",format='espresso-in',
                   input_data={'control': control,
                              'system': system,
                              'electrons': electrons,
                              'ions': ions,
                              'cell': cell},
                   pseudopotentials=atomic_species,
                   kpts=kpts)
FindAndReplace("ExecuteAndWait", "zzz", prefix)

