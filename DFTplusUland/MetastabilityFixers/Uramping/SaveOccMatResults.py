import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np
from functools import partial
from json_tricks import dumps, loads #the json module doesn't support non-standard types (such as the output from MAPI),
                                     #but json_tricks does
from Style import Article
Article()
def SaveDictAsJSON(fileName, dictionary, indent=4):
	with open(fileName+".json", "w") as f:
		f.write(dumps(dictionary, indent=indent)) #don't need to read this since it's just a 'checkpoint'

def ReadJSONFile(fileName):
	with open(fileName+".json", "r") as f:
		return loads(f.read()) #loads() returns the string fr


def PrepareData(UpOccMatFilename, DownOccMatFilename):
	UpOccMat = ReadJSONFile(UpOccMatFilename)
	DownOccMat = ReadJSONFile(DownOccMatFilename)
	
	preparedData = []
	for i in range(len(list(UpOccMat.keys()))):
		#preparedData[list(UpOccMat.keys())[i]] = [list(UpOccMat.values())[i],list(DownOccMat.values())[i]]
		preparedData.append({list(UpOccMat.keys())[i]: [list(UpOccMat.values())[i],list(DownOccMat.values())[i]]})
	return preparedData


def updateFrame(occMatData):

	UVal = 	list(occMatData.keys())[-1]
	spinUpData = list(occMatData.values())[0][0] #I couldn't tell you why, but the values of occMatData come out as 3D arrays - you need to use two indices to get a 1D array out
	spinDownData = list(occMatData.values())[0][1]
	
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
	fig.suptitle(f"U={UVal}")

	print(UVal)
	if(UVal=="0.0" or UVal=="4.0"):
		print("Plotting time")
		plt.savefig(f"U_{UVal}_URamping.png", dpi=300)

fig = plt.figure(figsize=(12, 7))
axUp = fig.add_subplot(1,2,1)
axDown = fig.add_subplot(1,2,2)	
preparedData = PrepareData("UpOccNos", "DownOccNos")
fps=5
noOfSecondsForFinalFrame=3
noOfAdditionalFrames=fps*noOfSecondsForFinalFrame
additionalFrames = [preparedData[-1]]*noOfAdditionalFrames
preparedData.extend(additionalFrames)

ani = animation.FuncAnimation(fig, updateFrame, frames=preparedData, interval=200)
writergif = animation.PillowWriter(fps=5) 
ani.save("Occupations.gif", writer=writergif)
