import os
import glob
import shutil
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-s", "--step", type=float, help="Increment for increasing U for U-ramping")
args = parser.parse_args()

stepVal = args.step

dirs = glob.glob("SR*")

def FindAndReplace(fileName, strToFind, strToReplace):
	with open(fileName, "r") as file:
		fileData = file.read()

	fileData = fileData.replace(strToFind, strToReplace)
	with open(fileName, "w") as file:
		file.write(fileData)

if(len(dirs)==0):
	newVal = 0.0
	newDirName = f"SR{newVal}"
	os.mkdir(newDirName)
	shutil.copy("Template/INCAR", newDirName)
	FindAndReplace(f"{newDirName}/INCAR", "yyy", str(newVal))
	shutil.copy("Template/KPOINTS", newDirName)
	shutil.copy("Template/POSCAR", newDirName)
	shutil.copy("Template/POTCAR", newDirName)
else:
	dirs = [directory.replace("SR", "") for directory in dirs]
	dirs.sort()
	latestVal = float(dirs[-1])
	latestDirName = f"SR{latestVal}"
	newVal = float(f"{latestVal+stepVal:.1f}") #ensures the numbers generated aren't incredibly long due to addition errors
	newDirName = f"SR{newVal}"
	os.mkdir(f"SR{newVal}")

	shutil.copy("Template/INCAR", newDirName)
	FindAndReplace(f"{newDirName}/INCAR", "yyy", str(newVal))
	shutil.copy("Template/KPOINTS", newDirName)
	shutil.copy("Template/POTCAR", newDirName)

	shutil.copy(f"{latestDirName}/CONTCAR", newDirName)
	os.rename(f"{newDirName}/CONTCAR", f"{newDirName}/POSCAR")
	
	shutil.copy(f"{latestDirName}/CHGCAR", newDirName)
	shutil.copy(f"{latestDirName}/WAVECAR", newDirName)

print(newDirName)
