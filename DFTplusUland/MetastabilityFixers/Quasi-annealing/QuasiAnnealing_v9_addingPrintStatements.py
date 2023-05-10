#!/usr/bin/env python3

#V2 - adds 'resume from' functionality
#V3 - checks if a structure relaxation has converged, and if not, the loop will break and I'll receive an email
#V4 - now a perturbed structure is only used for the first structure relaxation of a run after Run1. Afterwards, the original structure is used for restoration.
#V5 - Editing the script so that it works inside a slurm job script
#V6 - Implemented changes as stated in workflow diagram.
#V7 - Each run will use a distorted version of the structure found at the end of the last structure relaxation of the previous run. This version also implements a new convergence checking method using pymatgen. Also, changed BatchAndWait name to ExecuteAndWait
#V8 - Fixed the paths given to read in final energy values of runs
#V9 - added print statements to accompany any emailing. Also, added in division by number of sites in second loop (for runs after the first one) - this wasn't there previously. Also added a check to see if POSCAR_perturbed already exists, so as to not keep overwriting it everytime I batch the script.

import os
import shutil
import numpy as np
from pymatgen.core.structure import Structure
from pymatgen.io.vasp.outputs import Vasprun

def ConvergenceChecking():
    vasprunObj = Vasprun("vasprun.xml")
    return vasprunObj.converged

def GetNumSites():
    struct = Structure.from_file("POSCAR")
    return struct.num_sites

def FindAndReplace(fileName, strToFind, strToReplace):
    strToFind = str(strToFind)
    strToReplace = str(strToReplace)
    with open(fileName, "r") as file:
            fileData = file.read()

    fileData = fileData.replace(strToFind, strToReplace)
    with open(fileName, "w") as file:
            file.write(str(fileData))

energyConvCriterion = 0.0001
print("QA starting.")
os.chdir("SRTemplate")
numSites = GetNumSites()
os.chdir("..")
maxNoOfRuns = 10 #setting this to 2 temporarily to check if energy difference code works
energyDiff = 100 #needs to start off as some number greater than 10^-3
EDIFFlist = [0.05, 0.04, 0.03, 0.02, 0.01, 0.001]
POTIMlist = [1.0, 0.8, 0.6, 0.4, 0.2, 0.2] #final POTIM value is repeated so that POTIMlist and EDifflist have the same length
runNo = 1
while(energyDiff >= energyConvCriterion and len(POTIMlist)==len(EDIFFlist)):
    if(runNo>maxNoOfRuns): #program does final run (value of maxNoOfRuns), then at the end of the loop increases runNo by 1, exceeding the max no. of runs. Then, the while loop will break.
        os.system(f'echo "Maximum job no. ({maxNoOfRuns}) for job {SRdirName} reached" | mail -s "Quasi-annealing" rated.beta@gmail.com')
        print(f'echo "Maximum job no. ({maxNoOfRuns}) for job {SRdirName} reached" | mail -s "Quasi-annealing" rated.beta@gmail.com')
        break
    runDirName = f"Run{runNo}"
    if(not os.path.exists(runDirName)): #only try to create a new Run directory if it doesn't already exist
        os.mkdir(runDirName)
    os.chdir(runDirName)
    if(runNo == 1):
        for i in range(len(POTIMlist)):
            SRdirName = f"SR_{runNo}_{POTIMlist[i]}_{EDIFFlist[i]}"
            if(os.path.isfile(f"{SRdirName}/OUTCAR")):
                pass
            else:
                os.mkdir(SRdirName)
                os.chdir(SRdirName)
                
                #copying and replacing values
                shutil.copy("../../SRTemplate/POSCAR", ".")
                shutil.copy("../../SRTemplate/POTCAR", ".")
                shutil.copy("../../SRTemplate/KPOINTS", ".")
                shutil.copy("../../SRTemplate/INCAR", ".")
                FindAndReplace("INCAR", "zzz", EDIFFlist[i])
                FindAndReplace("INCAR", "yyy", POTIMlist[i])
                if(SRdirName!=f"SR_{runNo}_{POTIMlist[0]}_{EDIFFlist[0]}"): #if this isn't the first structure relaxation of the run, copy WAVECAR and CHGCAR from previous structure relaxation of the run
                    shutil.copy(f"../../Run{runNo}/SR_{runNo}_{POTIMlist[i-1]}_{EDIFFlist[i-1]}/WAVECAR", ".")
                    shutil.copy(f"../../Run{runNo}/SR_{runNo}_{POTIMlist[i-1]}_{EDIFFlist[i-1]}/CHGCAR", ".")
                
                os.system("../../ExecuteAndWait") #Executing

                convergenceChecker = ConvergenceChecking()
                if(convergenceChecker!=True):
                    os.system(f'echo "Structure relaxation {SRdirName} did not converge." | mail -s "Quasi-annealing" rated.beta@gmail.com')
                    print(f'echo "Structure relaxation {SRdirName} did not converge." | mail -s "Quasi-annealing" rated.beta@gmail.com')
                    break #Note - this will only break the for loop. However, since the next Run will not have the files it needs to begin, it will scream and die and the program will be terminated.

                os.chdir("..")

        finalSRdir = f"SR_{runNo}_{POTIMlist[-1]}_{EDIFFlist[-1]}"
        os.chdir(finalSRdir)
        finalEnergy = float(os.popen("grep TOTEN OUTCAR | tail -1 | awk '{print $5}'").read())/numSites #calculating energy per atom here
        with open("../FinalEnergy", "w") as file: #saving file in the Run directory, NOT the final SR directory for a given run
            file.write(str(finalEnergy))
        if(not os.path.isfile("POSCAR_perturbed")):
            os.system("../../DistortStruct.py")
        os.chdir("..")
        os.chdir("..") #this gets us back to the working directory of this workflow
    
    else:
        for i in range(len(POTIMlist)):
            SRdirName = f"SR_{runNo}_{POTIMlist[i]}_{EDIFFlist[i]}"
            if(os.path.isfile(f"{SRdirName}/OUTCAR")):
                pass
            else:
                
                os.mkdir(SRdirName)
                os.chdir(SRdirName)                

                #copying and replacing values
                shutil.copy(f"../../Run{runNo-1}/SR_{runNo-1}_{POTIMlist[-1]}_{EDIFFlist[-1]}/POSCAR_perturbed", ".") #Using the distorted structure of the final structure from previous run as the basis of structure restoration for the current run
                print(os.getcwd())
                posDiff=os.popen(f"diff POSCAR_perturbed ../../Run{runNo-1}/SR_{runNo-1}_{POTIMlist[-1]}_{EDIFFlist[-1]}/POSCAR_perturbed").read()
                print(f'posDiff:\n{posDiff}')
                os.rename("POSCAR_perturbed", "POSCAR")
                shutil.copy("../../SRTemplate/POTCAR", ".")
                shutil.copy("../../SRTemplate/KPOINTS", ".")
                shutil.copy("../../SRTemplate/INCAR", ".")
                FindAndReplace("INCAR", "zzz", EDIFFlist[i])
                FindAndReplace("INCAR", "yyy", POTIMlist[i])
                
                if(i==0): #only for the first relaxation of a run is a distorted structure necessary
                    #copying WAVECAR and CHGCAR from previous run
                    shutil.copy(f"../../Run{runNo-1}/SR_{runNo-1}_{POTIMlist[-1]}_{EDIFFlist[-1]}/WAVECAR", ".")
                    shutil.copy(f"../../Run{runNo-1}/SR_{runNo-1}_{POTIMlist[-1]}_{EDIFFlist[-1]}/CHGCAR", ".")
                else:
                    shutil.copy(f"../../Run{runNo}/SR_{runNo}_{POTIMlist[i-1]}_{EDIFFlist[i-1]}/WAVECAR", ".")
                    shutil.copy(f"../../Run{runNo}/SR_{runNo}_{POTIMlist[i-1]}_{EDIFFlist[i-1]}/CHGCAR", ".")

                os.system("../../ExecuteAndWait") #Executing
                
                convergenceChecker = ConvergenceChecking()
                if(convergenceChecker!=True):
                    os.system(f'echo "Structure relaxation {SRdirName} did not converge." | mail -s "Quasi-annealing" rated.beta@gmail.com')
                    print(f'echo "Structure relaxation {SRdirName} did not converge." | mail -s "Quasi-annealing" rated.beta@gmail.com')
                    break #Note - this will only break the for loop. However, since the next Run will not have the files it needs to begin, it will scream and die and the program will be terminated.
                
                os.chdir("..")

        finalSRdir = f"SR_{runNo}_{POTIMlist[-1]}_{EDIFFlist[-1]}"
        os.chdir(finalSRdir)
        finalEnergy = float(os.popen("grep TOTEN OUTCAR | tail -1 | awk '{print $5}'").read())/numSites
        with open("../FinalEnergy", "w") as file: #saving file in the Run directory, NOT the final SR directory for a given run
            file.write(str(finalEnergy))
        if(not os.path.isfile("POSCAR_perturbed")):
            os.system("../../DistortStruct.py")
        os.chdir("..")
        os.chdir("..") #this gets us back to the working directory of this workflow

        #now that we're back in the working directory of this workflow, we can calculate the energy difference between this run and the previous run
        prevEnergy = np.loadtxt(f"Run{runNo-1}/FinalEnergy") #runNo-1 , i.e. we're looking at the previous Run directory
        currentEnergy = np.loadtxt(f"Run{runNo}/FinalEnergy")
        energyDiff = abs(currentEnergy-prevEnergy)
    runNo+=1

if(energyDiff < energyConvCriterion): #now using 0.1 meV/atom as the convergence criterion
    os.system('echo "" | mail -s "QA finished" rated.beta@gmail.com')
    print(f"QA finished. Ediff was: {energyDiff} eV")
else:
    os.system('echo "" | mail -s "QA broke" rated.beta@gmail.com')
    print("QA broke.")