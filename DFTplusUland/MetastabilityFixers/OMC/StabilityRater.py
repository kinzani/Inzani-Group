import numpy as np

occEnergies = np.loadtxt("EnergyVals_OMC")
magQnos = list(np.arange(-3, 4))

energiesAndQnos = dict(zip(occEnergies, magQnos))

sortedEnergies = np.sort(list(energiesAndQnos.keys()))
lowestEnergy = sortedEnergies[0]
for i in sortedEnergies:
	print(f"{energiesAndQnos[i]} | {i:.8f} | {i-lowestEnergy:.8e}")
	#print()
	
