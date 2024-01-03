#!/usr/bin/env python3
import glob
import os
import numpy as np
import shutil

def CheckStructureDiffsLessThanTol(stepNo, tol=1.):
    diffs=np.array(list(map(float, str(os.popen(f"cpos CONTCAR POSCAR | grep diff | awk '{{print $2 \" \" $3 \" \" $4}}'").read()).replace("\n","").split()))) #compare POSCAR for this step to previous step's POSCAR
    boolean=np.all(diffs <= tol)
    return boolean, diffs

def FindAndReplace(fileName, strToFind, strToReplace):
    strToFind = str(strToFind)
    strToReplace = str(strToReplace)
    with open(fileName, "r") as file:
            fileData = file.read()

    fileData = fileData.replace(strToFind, strToReplace)
    with open(fileName, "w") as file:
            file.write(str(fileData))

def CopyOverInputFiles(stepNo): #all files except POSCAR - that can't simply be copied over so easily
    files = ["INCAR", "POTCAR", "KPOINTS"]
    for file in files:
        shutil.copy(file, f"Step{stepNo}")



calcNum = 1
while(True):
    print(calcNum)
    relaxDirs=glob.glob("Step*")
    if(len(relaxDirs)==0):
        print("Hello")
        os.mkdir(f"Step{calcNum}")
        CopyOverInputFiles(calcNum)
        os.chdir(f"Step{calcNum}")
        shutil.copy("../POSCAR", ".")
        FindAndReplace("INCAR", "yyy", 2) #setting ISIF to 2 - only atom positions can change
        os.system("../ExecuteAndWaitSTD")
    else:
        calcNum=max(list(map(int, [step.replace("Step", "") for step in relaxDirs])))
        calcNum += 1
        os.mkdir(f"Step{calcNum}")
        CopyOverInputFiles(calcNum)
        os.chdir(f"Step{calcNum}")
        FindAndReplace("INCAR", "yyy", 3) #setting ISIF to 3 - variable cell relaxation
        shutil.copy(f"../Step{calcNum-1}/CONTCAR", "POSCAR")
        os.system("../ExecuteAndWaitSTD")
    print(f"Completed calc no. {calcNum}.")
    if(calcNum >= 3):
        convergedStructStatus, diffs = CheckStructureDiffsLessThanTol(calcNum)
        if(convergedStructStatus == True):
            print(diffs)
            print(f"Converged after {calcNum} steps.")
            os.chdir("..")
            break
        else:
            print("Structure has not converged. Moving onto the next step.")
    os.chdir("..")
