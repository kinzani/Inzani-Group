#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
import os
import glob
from json_tricks import dumps, loads #the json module doesn't support non-standard types (such as the output from MAPI),
                                     #but json_tricks does

def SaveDictAsJSON(fileName, dictionary, indent=4):
    with open(fileName+".json", "w") as f:
        f.write(dumps(dictionary, indent=indent)) #don't need to read this since it's just a 'checkpoint'

def ReadJSONFile(fileName):
    with open(fileName+".json", "r") as f:
        return loads(f.read()) #loads() returns the string fr

def OccupancyGetter(occMatFileName):
    occMat = np.loadtxt(occMatFileName)
    occMat = np.matrix(occMat)
    Diag = np.diag(occMat)

    return Diag



UpOccNos = {}
DownOccNos = {}
os.system("sed -n '/onsite density matrix/,/occupancies/p' OUTCAR | tail -21 | head -n 19 > OccMats")
os.system("sed -n '/spin component  1/,/spin component  2/p' OccMats | head -n 9 | tail -7 > UpMat")
os.system("cat OccMats | tail -7 > DownMat")
UpOccNos = OccupancyGetter("UpMat")
DownOccNos = OccupancyGetter("DownMat")

SaveDictAsJSON("UpOccNos", UpOccNos)
SaveDictAsJSON("DownOccNos", DownOccNos)


import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
from functools import partial
from json_tricks import dumps, loads #the json module doesn't support non-standard types (such as the output from MAPI),
                                     #but json_tricks does
def SaveDictAsJSON(fileName, dictionary, indent=4):
	with open(fileName+".json", "w") as f:
		f.write(dumps(dictionary, indent=indent)) #don't need to read this since it's just a 'checkpoint'

def ReadJSONFile(fileName):
	with open(fileName+".json", "r") as f:
		return loads(f.read()) #loads() returns the string fr


def PrepareData(UpOccMatFilename, DownOccMatFilename):
	UpOccMat = list(ReadJSONFile(UpOccMatFilename))
	DownOccMat = list(ReadJSONFile(DownOccMatFilename))
	
	preparedData = []
	preparedData.append(UpOccMat)
	preparedData.append(DownOccMat)
	return preparedData


def updateFrame(occMatData):
	UVal = 	list(occMatData.keys())[-1]
	spinUpData = list(occMatData[0]) #I couldn't tell you why, but the values of occMatData come out as 3D arrays - you need to use two indices to get a 1D array out
	spinDownData = list(occMatData[1])
	
	fig.tight_layout(pad=1.0)
	axUp.clear()
	axDown.clear()
	axUp.set_ylim([0.0, 1.0])
	axDown.set_ylim([0.0, 1.0])
	orbitals = [r"$f_{-3}$", r"$f_{-2}$", r"$f_{-1}$", r"$f_{0}$", r"$f_{1}$", r"$f_{2}$", r"$f_{3}$"]
	axUp.bar(orbitals, spinUpData)
	axDown.bar(orbitals, spinDownData)
	axUp.set_ylabel("Occupation no.")
	axUp.title.set_text("Spin up")
	axDown.title.set_text("Spin down")
	plt.savefig("OccNos.png", dpi=300)

fig = plt.figure(figsize=(12, 7))
axUp = fig.add_subplot(1,2,1)
axDown = fig.add_subplot(1,2,2)	
preparedData = PrepareData("UpOccNos", "DownOccNos")
spinUpData=preparedData[0]
spinDownData=preparedData[1]

fig.tight_layout(pad=1.0)
axUp.clear()
axDown.clear()
axUp.set_ylim([0.0, 1.0])
axDown.set_ylim([0.0, 1.0])
orbitals = [r"$f_{-3}$", r"$f_{-2}$", r"$f_{-1}$", r"$f_{0}$", r"$f_{1}$", r"$f_{2}$", r"$f_{3}$"]
axUp.bar(orbitals, spinUpData)
axDown.bar(orbitals, spinDownData)
axUp.set_ylabel("Occupation no.")
axUp.title.set_text("Spin up")
axDown.title.set_text("Spin down")

spinUpDataNegative=[abs(data) if data < 0 else 0 for data in spinUpData]
spinDownDataNegative=[abs(data) if data < 0 else 0 for data in spinDownData]
if(len(spinUpDataNegative)!=0):
	axUp.bar(orbitals, spinUpDataNegative)
if(len(spinDownDataNegative)!=0):
	axDown.bar(orbitals, spinDownDataNegative)

plt.savefig("OccNos.png", dpi=300)
