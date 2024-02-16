from pymatgen.io.vasp.outputs import Vasprun
from pymatgen.analysis.phase_diagram import PhaseDiagram, PDPlotter
from pymatgen.apps.borg.hive import VaspToComputedEntryDrone
from pymatgen.entries.compatibility import MaterialsProject2020Compatibility
import os
from pymatgen.ext.matproj import MPRester
import argparse
import warnings
warnings.filterwarnings("ignore")

parser = argparse.ArgumentParser(prog = 'Phase diagram plotter',
                    description = 'This program takes a vasprun.xml and adds the result into a phase diagram for the structure used in the original calculation.')
parser.add_argument("-f", "--file", type=str, default="vasprun.xml", help="Path to a vasprun.xml file.")
args = parser.parse_args()
vasprunFile = args.file

def APIkeyChecker():
    APIkey = None #done so that APIkey is not lost in the scope of the with block
    if(not os.path.isfile("APIkey.txt")): #if APIkey.txt doesn't exist, ask for key and create txt file
        print("\nIt seems you do not have an API key saved.")
        while(True):
            APIkey = input("\nPlease input your API key: ")
            print(f"Testing your given API key: {APIkey}")
            with MPRester(APIkey) as mpr:
                try:
                    mpr.get_structure_by_material_id("mp-149")
                    print("API key is valid. Saving API key.")
                    with open('APIkey.txt', 'w') as f:
                        f.write(APIkey)
                        return APIkey
                    break
                except:
                    print(f"API key {APIkey} was invalid.")

    else:
        with open("APIkey.txt", "r") as f:
            APIkey= f.read()
            return APIkey

print("Starting vasprun things:")
vasprunObj = Vasprun(vasprunFile)
elemSymbols = list(dict.fromkeys(vasprunObj.atomic_symbols)) #keeping one of each of the element symbols
print(f"Elements in material: {elemSymbols}")
mpr = MPRester(APIkeyChecker())
entries = mpr.get_entries_in_chemsys(elemSymbols)

#code HEAVILY INSPIRED by this github page: https://gist.github.com/shyuep/3570304
drone = VaspToComputedEntryDrone()
entry = drone.assimilate(".") #looking for vasprun.xml file in current working directory
compat = MaterialsProject2020Compatibility()
processedEntry = compat.process_entry(entry) #returns a computed entry if compatible, None otherwise. Refer to this page for compatability: https://pymatgen.org/usage.html , and then this page for information on data sets that can be used to make a calculation compatible: https://pymatgen.org/pymatgen.io.vasp.sets.html#module-pymatgen.io.vasp.sets
if not processedEntry: #if processedEntry returns None (incompatible result)
        print("Calculation parameters are not consistent with Materials Project parameters. Still, we press on.")
        entries.append(entry)
        pd=PhaseDiagram(entries)
        ehull = pd.get_e_above_hull(entries[-1])
        print(f"Energy above hull (uncorrected due to incompatibility with Materials Project parameters) for {entries[-1].composition}: {ehull:.3f} eV/atom")   
else:
    print("Entry is compatibile with Materials Project parameters.")
    entries.append(processedEntry)
    pd=PhaseDiagram(entries)
    ehull = pd.get_e_above_hull(entries[-1])
    print(f"Energy above hull (corrected) for {entries[-1].composition}: {ehull:.3f} eV/atom")

plotter = PDPlotter(pd, show_unstable=True)
plotter.show()