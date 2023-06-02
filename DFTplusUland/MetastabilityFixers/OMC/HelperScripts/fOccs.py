#!/usr/bin/env python3
import numpy as np
import os

def OccupancyGetter(occMatFileName):
    occMat = np.loadtxt(occMatFileName)
    occMat = np.matrix(occMat)
    Diag = np.diag(occMat)

    print(Diag)
    print(np.sum(Diag))
    return np.sum(Diag)

if(os.path.isfile("OUTCAR")):
    os.system("sed -n '/onsite density matrix/,/occupancies/p' OUTCAR | tail -21 | head -n 19 > OccMats")
    os.system("sed -n '/spin component  1/,/spin component  2/p' OccMats | head -n 9 | tail -7 > UpMat")
    os.system("cat OccMats | tail -7 > DownMat")

    print("Spin up")
    upTot=OccupancyGetter("UpMat")
    print()
    print("Spin down")
    downTot=OccupancyGetter("DownMat")
    print()
    print(f"Total e- count: {upTot+downTot}")
    os.system("rm OccMats")
    os.system("rm UpMat")
    os.system("rm DownMat")
else:
    print("OUTCAR file not found. Maybe you're in the wrong directory?")
