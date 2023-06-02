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
    print(occMat)
    print(occMat[0,0])
    occMat = np.matrix(occMat)
    Diag = np.diag(occMat)

    print()
    print(Diag)
    print(np.sum(Diag))
    print()
    return Diag

UVals = glob.glob("SR*")
UVals = [directory.replace("SR", "") for directory in UVals]
UVals.sort()
UVals = [float(i) for i in UVals]
print(UVals)


UpOccNos = {}
DownOccNos = {}
for U in UVals:
	os.chdir(f"SR{U}")
	os.system("sed -n '/onsite density matrix/,/occupancies/p' OUTCAR | tail -21 | head -n 19 > OccMats")
	os.system("sed -n '/spin component  1/,/spin component  2/p' OccMats | head -n 9 | tail -7 > UpMat")
	os.system("cat OccMats | tail -7 > DownMat")
	UpOccNos[U] = OccupancyGetter("UpMat")
	DownOccNos[U] = OccupancyGetter("DownMat")
	os.chdir("..")

SaveDictAsJSON("UpOccNos", UpOccNos)
SaveDictAsJSON("DownOccNos", DownOccNos)



