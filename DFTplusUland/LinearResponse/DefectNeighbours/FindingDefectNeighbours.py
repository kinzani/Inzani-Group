from pymatgen.core.structure import Structure
from pymatgen.io.vasp.inputs import Poscar

def FindAndReplace(fileName, strToFind, strToReplace):
    strToFind = str(strToFind)
    strToReplace = str(strToReplace)
    with open(fileName, "r") as file:
            fileData = file.read()

    fileData = fileData.replace(strToFind, strToReplace)
    with open(fileName, "w") as file:
            file.write(str(fileData))

def FindImage(site, structure):
    """
    So, funny story - if you try to get the index of a neighbour of a site using the original structure you got the neighbours from,
    Python may scream at you, because the neighbour you have is an image of a site that's within the structure. This function finds
    the relevant image in the structure and returns that.
    
    site - neighbor object which you want to find the image of inside the structure it came from.
    structure - the structure you're analysing.
    """
    return next(image for image in structure if site.is_periodic_image(image)) #next() function acts like list comprehension, but only returns the first instance that matches the if statement given

def ReturnNeighborIndices(struct, siteIndex, distFromSite):
    """
    :struct - structure object
    :siteIndex - the index of the site of which you want to find neighbours of
    :distFromSite - the radius in Angstrom of which you're looking for neighbours around the site with index siteIndex
    """
    
    neighbourIndices={}
    for site in struct.get_neighbors(struct[siteIndex], distFromSite):
        try:
            neighbourIndex=struct.index(site)
        except ValueError:
            image=FindImage(site,struct)
            neighbourIndex=struct.index(image)
        #neighbourIndices.append(neighbourIndex)
        neighbourIndices[neighbourIndex]=site
    return neighbourIndices

def GetListOfElementSitesFromStructure(elementSymbol, struct):
    atoms = [site for site in struct if site.species_string==elementSymbol]
    return atoms

def GetListOfElementIndicesFromStructure(elementSymbol: str, struct) -> list:
    sites = GetListOfElementSitesFromStructure(elementSymbol, struct)
    elementSiteIndicies = [struct.index(site) for site in sites]
    return elementSiteIndicies

def CouplingNeighbourAndStructIndices(elementIndices: list[int], neighbourIndices: list[int]) -> list[tuple]:
    """
    Couples a list of indices for a given element in a structure to a list of indices of neighbours of the same element and removes overlapping indices.
    This is so that if a neighbour atom is already at the top of its element list in the structure, then it doesn't need to be moved.
    """
    min_length = min(len(elementIndices), len(neighbourIndices))
    elementIndices = elementIndices[:min_length]
    neighbourIndices = neighbourIndices[:min_length]
    overlappingIndices=list(set(elementIndices) & set(neighbourIndices))
    elementIndices=[index for index in elementIndices if index not in overlappingIndices]
    neighbourIndices=[index for index in neighbourIndices if index not in overlappingIndices]
    couplingIndices=list(zip(elementIndices, neighbourIndices)) #apparently after you iterate over a zip once, it gets emptied https://stackoverflow.com/questions/17777219/zip-variable-empty-after-first-use
    return couplingIndices

struct = Structure.from_file("YAG_SC_doped.vasp")

yttriums = [site for site in struct if site.species_string=="Y"]
oxygens = [site for site in struct if site.species_string=="O"]

YsiteIndicies = [struct.index(site) for site in yttriums]
OsiteIndicies = [struct.index(site) for site in oxygens]

YsiteIndicies=GetListOfElementIndicesFromStructure("Y", struct)
OsiteIndicies=GetListOfElementIndicesFromStructure("O", struct)

CeNeighbours = ReturnNeighborIndices(struct, 159, 4)

YsitesInCeNeighbours=[index for index in CeNeighbours if CeNeighbours[index].species_string=="Y"]
OsitesInCeNeighbours=[index for index in CeNeighbours if CeNeighbours[index].species_string=="O"]

couplingYindices=CouplingNeighbourAndStructIndices(YsiteIndicies, YsitesInCeNeighbours)
couplingOindices=CouplingNeighbourAndStructIndices(OsiteIndicies, OsitesInCeNeighbours)

#Converting all Y to Ne, then moving them to the top of the Y list
for index in YsitesInCeNeighbours:
    struct.replace(index, "Ne")

for structIndex, neighbourIndex in couplingYindices:
    struct[structIndex], struct[neighbourIndex]=struct[neighbourIndex],struct[structIndex]

#replacing O neighbours with He
for index in OsitesInCeNeighbours:
    struct.replace(index, "He")

#I already replaced the O neighbours to Ar, so now all I need to do is move those neighbours to the top of the O list
for structIndex, neighbourIndex in couplingOindices:
    struct[structIndex], struct[neighbourIndex]=struct[neighbourIndex],struct[structIndex]

print(struct)

Poscar(struct).write_file("CeNeighbours.vasp", significant_figures=16)

FindAndReplace("CeNeighbours.vasp", "He", "O")
FindAndReplace("CeNeighbours.vasp", "Ne", "Y")