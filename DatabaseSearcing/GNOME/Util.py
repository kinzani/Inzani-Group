from json_tricks import dumps, loads #the json module doesn't support non-standard types (such as the output from MAPI),
                                     #but json_tricks does
import sys, os
import pandas as pd
from pymatgen.core.periodic_table import Element
import numpy as np

#Functions used by MaterialSearchCore.py to prep GNOME data.
########################################
def get_NElems(elements):
    return len(list(elements))

def TurnElementsIntoList(elements):
    elements = elements.replace("[", "")
    elements = elements.replace("]", "")
    elements = elements.replace(",", "")
    elements = elements.replace("'", "")
    elements = elements.strip()
    elements = elements.split()
    return list(elements)
#########################################

def ConvertJSONresultsToExcel(JSONfileName): #do not need to give the .json extension - that's assumed
    results = ReadJSONFile(JSONfileName)
    df = pd.DataFrame.from_dict(results)
    df.to_excel(f"{JSONfileName}.xlsx")

# Disable printing
def BlockPrint():
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

# Restore printing
def EnablePrint():
    sys.stdout = sys.__stdout__

def SaveDictAsJSON(fileName, dictionary, indent=4):
    with open(fileName+".json", "w") as f:
        f.write(dumps(dictionary, indent=indent)) #don't need to read this since it's just a 'checkpoint'

def ReadJSONFile(fileName):
    with open(fileName+".json", "r") as f:
        return loads(f.read()) #loads() returns the string from f.read() as dict

def ListOfTheElements(elementsExcluded=None):
    noOfElements = 118 #as of 2021
    atomicNos = np.arange(1, noOfElements+1) #the function stops just before the given value (default step = 1)
    
    if(elementsExcluded != None):
        atomicNos = [z for z in atomicNos if z not in elementsExcluded]
    
    symbolsTypeElement = [Element.from_Z(z) for z in atomicNos]
    symbols = [str(symbol) for symbol in symbolsTypeElement]
    
    return symbols