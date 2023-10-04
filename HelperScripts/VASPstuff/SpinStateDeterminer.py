#!/usr/bin/env python3
import os
import pandas as pd
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-o", "--outcar", type=str, default=".", help="The file path to the OUTCAR of the ground state calculation of your material.")
args = parser.parse_args()
if(args.outcar[-1]=="/"):
    args.outcar = args.outcar[:-1]
outcarPath = f"{args.outcar}/OUTCAR"

n_bands = int(os.popen(f"grep NBANDS {outcarPath} | awk '{{print $15}}'").read())
n_k = int(os.popen(f"grep NBANDS {outcarPath} | awk '{{print $4}}'").read())
print(f"Num of bands: {n_bands}")
print(f"Num of k-points: {n_k}")
endOfSpinComponentSection_lineNums=str(os.popen(f'grep -n " {n_bands}    " {outcarPath} | tail -1').read())
endOfSpinComponentSection_lineNums = endOfSpinComponentSection_lineNums.strip().split("\n")
endOfSpinComp = [int(line.split(":")[0]) for line in endOfSpinComponentSection_lineNums][0]
startOfSpinComp1=int(str(os.popen(f'grep -n "spin component 1" {outcarPath} | tail -1').read()).strip().split(":")[0])

spinComps = str(os.popen(f'sed -n "{startOfSpinComp1},{endOfSpinComp}p" {outcarPath} | tail -n +2').read()).strip().split("\n")

spinCompLines=[(line, i) for i,line in enumerate(spinComps) if "spin component" in line]
spinComp2_headlingLine=spinCompLines[-1][1] #-1 to get the second spin in case there's more than one, and the 1 index gets me the line number of the spin

spinComp1 = spinComps[:spinComp2_headlingLine]
spinComp2 = spinComps[spinComp2_headlingLine:]
del spinComp2[:2] #this removes the "spin component 2" header and a blank line - this was already removed from spinComp1


spinComp1=[line for line in spinComp1 if "band No." not in line]
spinComp1=[line for line in spinComp1 if line!=""]
spinComp2=[line for line in spinComp2 if "band No." not in line]
spinComp2=[line for line in spinComp2 if line!=""]

kpointInfo_1=[{int(line.split()[1]): list(map(float, line.split()[-3:]))} for line in spinComp1 if "k-point" in line] #the 1 index gets the k-point number, and [-3:] gets the coordinates of the k-points in reciprocal space
kpointInfo_2=[{int(line.split()[1]): list(map(float, line.split()[-3:]))} for line in spinComp2 if "k-point" in line]

spinComp1_kpointLineNums = [(line, i) for i,line in enumerate(spinComp1) if "k-point" in line]
spinComp2_kpointLineNums = [(line, i) for i,line in enumerate(spinComp2) if "k-point" in line]
spinComp1_kpointLineNums = [line[1] for line in spinComp1_kpointLineNums]
spinComp2_kpointLineNums = [line[1] for line in spinComp2_kpointLineNums]


spinComps = [spinComp1, spinComp2]
spinKpointLineNums = [spinComp1_kpointLineNums, spinComp2_kpointLineNums]

spinComp1res = {}
spinComp2res = {}
for spinNum, spinComp in enumerate(spinComps):
    for i in range(len(spinKpointLineNums[spinNum])): #spinKpointLineNums[spinNum] has a length equal to the number of k-points
        currentLineNum=spinKpointLineNums[spinNum][i]+1 #+1 because the actual current line is the k-point header line - we want to skip that
        if(i==len(spinKpointLineNums[spinNum])-1):#last iteration
            nextLineNum=None #setting the endpoint of a slice as None is the same as leaving the endpoint blank, i.e. slicing until the end of the list - -1 slices until the penultimate element in the list
        else:
            nextLineNum=spinKpointLineNums[spinNum][i+1]
        rawKpointInfo=[line.strip().split() for line in spinComp[currentLineNum:nextLineNum]]
        bandNums, bandEnergies, occs = pd.DataFrame(rawKpointInfo).T.values.tolist()
        bandNums = [int(i) for i in bandNums]
        occs = [float(occ) for occ in occs]
        bandEnergies = [float(energy) for energy in bandEnergies]
        if(spinNum==0):
            spinComp1res[i+1] = {"band_num": bandNums, "band_E": bandEnergies, "occs": occs}
        elif(spinNum==1):
            spinComp2res[i+1] = {"band_num": bandNums, "band_E": bandEnergies, "occs": occs}
        else:
            print("How did you get here? You can only get here if you have more than two spin channels.")


#just looking at the first k-point since the band occupations are identical regardless of k-point
spinComp1_occs = spinComp1res[1]["occs"]
spinComp2_occs = spinComp2res[1]["occs"]
o_up=next(spinComp1_occs.index(x) for x in spinComp1_occs if x == 0.)
o_down=next(spinComp2_occs.index(x) for x in spinComp2_occs if x == 0.)
u_up = n_bands-o_up
u_down = n_bands-o_down
print(f"Spin channel 1:\n  Num of filled bands={o_up}\n  Num of empty bands={u_up}\n")
print(f"Spin channel 2:\n  Num of filled bands={o_down}\n  Num of empty bands={u_down}\n")

elecDiff = abs(o_up-o_down)
spinState = int(2*(1/2)*elecDiff+1)
if(o_up>o_down):
    print(f"Unpaired electrons in spin channel 1, num. of UPE = {elecDiff}, spin state = {spinState}")
elif(o_down>o_up):
    print(f"Unpaired electrons in spin channel 2, num. of UPE = {elecDiff}, spin state = {spinState}")
else:
    print(f"Material is diamagnetic, i.e. UPE = {elecDiff}. Spin state = {spinState}")