#!/usr/bin/env python3

import numpy as np
from Util import *

OMCandEnerg=ReadJSONFile("EnergyVals_OMC")
print(type(OMCandEnerg))
print(list(OMCandEnerg.keys()))
sortedOMCandEnerg={k: v for k, v in sorted(OMCandEnerg.items(), key=lambda item: item[1])} #code taken from here: https://stackoverflow.com/questions/613183/how-do-i-sort-a-dictionary-by-value

#sortedOMCandEnerg = np.sort(list(OMCandEnerg.keys()))
lowestEnergy = min(sortedOMCandEnerg.values())
energyDiffs = {}
for omcKey in list(sortedOMCandEnerg.keys()):
        print(f"{omcKey} | {OMCandEnerg[omcKey]} | {OMCandEnerg[omcKey]-lowestEnergy:.8e}")
        energyDiffs[omcKey] = [float(f"{OMCandEnerg[omcKey]-lowestEnergy:.8f}")]

SaveDictAsJSON("EnergyDiffs", energyDiffs)
