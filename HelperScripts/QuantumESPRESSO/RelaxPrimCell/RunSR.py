#!/usr/bin/env python3
import glob
import os
import numpy as np

def CheckStructureDiffsLessThanTol(stepNo, tol=1.):
    diffs=np.array(list(map(float, str(os.popen(f"cpos POSCAR ../Step{stepNo-1}/POSCAR | grep diff | awk '{{print $2 \" \" $3 \" \" $4}}'").read()).replace("\n","").split()))) #compare POSCAR for this step to previous step's POSCAR
    boolean=np.all(diffs <= tol)
    return boolean, diffs

if(not os.path.isdir(f"Step1")): #if Step1 does not exist, make it
    os.system("./CreateRelax_step1.py")
    os.chdir("Step1")
    os.system("./ExecuteAndWait")
    os.chdir("..")

while(True):
    os.system("./CreateVCrelax.py")
    relaxDirs=glob.glob("Step*")
    calcNum=int([step.replace("Step", "") for step in relaxDirs][-1])
    print(f"On calc no. {calcNum}.")
    os.chdir(f"Step{calcNum}")
    os.system("./ExecuteAndWait")
    os.system(f'echo "" | mail -s "Step{calcNum} completed" rated.beta@gmail.com')
    if(calcNum >= 3):
        os.system("ConvQEout2POSCAR.py") #Since a POSCAR is only made for a step when the next one is being made with the CreateVCrelax.py script, a POSCAR should be made now to check structure convergence
        convergedStructStatus, diffs = CheckStructureDiffsLessThanTol(calcNum)
        if(convergedStructStatus == True):
            print(diffs)
            print(f"Converged after {calcNum} steps.")
            os.chdir("..")
            break
        else:
            print("Structure has not converged. Moving onto the next step.")
    os.chdir("..")


