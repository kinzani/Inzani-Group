from pymatgen.core.structure import Structure
from pymatgen.io.vasp.inputs import Poscar
import statistics


def FindItemClosestToMean(someList: list[float]) -> float:
    mean=statistics.mean(someList)
    diffList = [abs(item-mean) for item in someList]
    smallestDiff=min(diffList)
    indexOfClosestItem=diffList.index(smallestDiff)
    return someList[indexOfClosestItem]

def GetMeanDistanceNeighbourSite(specialSite, neighbourSiteList):
    distsFromSpecialSite=[specialSite.distance(site) for site in neighbourSiteList]
    siteDistDict = dict(zip(distsFromSpecialSite, neighbourSiteList))
    meanSiteDist = FindItemClosestToMean(distsFromSpecialSite)
    meanNeighbourSite=siteDistDict[meanSiteDist]
    return meanNeighbourSite

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
    elementSiteIndices = [struct.index(site) for site in sites]
    return elementSiteIndices

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

def ReplaceAllElementsWithAnotherElement(elementSymbolToReplace, replacementElementSymbol, structure):
    indicesOfChosenElement=GetListOfElementIndicesFromStructure(elementSymbolToReplace, structure)
    for index in indicesOfChosenElement:
        structure.replace(index, replacementElementSymbol)

struct = Structure.from_file("YAG_SC_doped.vasp")
struct = struct.copy()
yttriums = [site for site in struct if site.species_string=="Y"]
oxygens = [site for site in struct if site.species_string=="O"]

YsiteIndices = [struct.index(site) for site in yttriums]
OsiteIndices = [struct.index(site) for site in oxygens]

YsiteIndices=GetListOfElementIndicesFromStructure("Y", struct)
OsiteIndices=GetListOfElementIndicesFromStructure("O", struct)

CeNeighbours = ReturnNeighborIndices(struct, 159, 4)

YsitesInCeNeighbours=[index for index in CeNeighbours if CeNeighbours[index].species_string=="Y"]
OsitesInCeNeighbours=[index for index in CeNeighbours if CeNeighbours[index].species_string=="O"]

couplingYindices=CouplingNeighbourAndStructIndices(YsiteIndices, YsitesInCeNeighbours)
couplingOindices=CouplingNeighbourAndStructIndices(OsiteIndices, OsitesInCeNeighbours)

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


struct
yttriums = [site for site in struct if site.species_string=="Y"]
oxygens = [site for site in struct if site.species_string=="O"]

YsiteIndices = [struct.index(site) for site in yttriums]
OsiteIndices = [struct.index(site) for site in oxygens]

YsiteIndices=GetListOfElementIndicesFromStructure("Y", struct)
OsiteIndices=GetListOfElementIndicesFromStructure("O", struct)

CeNeighbours = ReturnNeighborIndices(struct, 159, 4)

YsitesInCeNeighbours=[index for index in CeNeighbours if CeNeighbours[index].species_string=="Y"]
OsitesInCeNeighbours=[index for index in CeNeighbours if CeNeighbours[index].species_string=="O"]

couplingYindices=CouplingNeighbourAndStructIndices(YsiteIndices, YsitesInCeNeighbours)
couplingOindices=CouplingNeighbourAndStructIndices(OsiteIndices, OsitesInCeNeighbours)

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
    
distalYttriums = [site for site in struct if site.species_string=="Y"]
distalOxygens = [site for site in struct if site.species_string=="O"]
distalYsiteIndices = [struct.index(site) for site in distalYttriums]
distalOsiteIndices = [struct.index(site) for site in distalOxygens]

proximalYttriums = [site for site in struct if site.species_string=="Ne"]
proximalOxygens = [site for site in struct if site.species_string=="He"]
proximalYsiteIndices = [struct.index(site) for site in proximalYttriums]
proximalOsiteIndices = [struct.index(site) for site in proximalOxygens]


Ce = struct[-1]

proximalYdists=[Ce.distance(Ysite) for Ysite in proximalYttriums]
proximalYdistDict = dict(zip(proximalYdists, proximalYttriums))

meanProximalYdist = FindItemClosestToMean(proximalYdists)
meanProximalYneighbour=proximalYdistDict[meanProximalYdist]
meanProximalYneighbour

meanProximalYNeighbour=GetMeanDistanceNeighbourSite(Ce, proximalYttriums)
meanDistalYNeighbour=GetMeanDistanceNeighbourSite(Ce, distalYttriums)
meanProximalONeighbour=GetMeanDistanceNeighbourSite(Ce, proximalOxygens)
meanDistalONeighbour=GetMeanDistanceNeighbourSite(Ce, distalOxygens)

meanNeighbours = [meanProximalYNeighbour, meanDistalYNeighbour, meanProximalONeighbour, meanDistalONeighbour]
oldSymbolsToNewSymbols={"Ne": "Y", "He": "O"}
distalOrProximalBySymbol={"Ne": "proximal", "Y": "distal", "He": "proximal", "O": "distal"}
for meanNeighbour in meanNeighbours:
    structCopy=struct.copy()
    meanNeighbourSymbol=meanNeighbour.species_string
    meanNeighbourIndex=structCopy.index(meanNeighbour)
    proxOrDistTag=distalOrProximalBySymbol[meanNeighbourSymbol]
    structCopy.replace(meanNeighbourIndex, "Og")
    ReplaceAllElementsWithAnotherElement("Ne", "Y", structCopy)
    ReplaceAllElementsWithAnotherElement("He", "O", structCopy)
    
    #proximal atoms have non-normal symbols (He or Ne), and since I already did the atom replacement above,
    #I need to convert the symbol I'm looking for to the normal symbols - Y/O
    if(meanNeighbourSymbol in list(oldSymbolsToNewSymbols.keys())): 
        meanNeighbourSymbol=oldSymbolsToNewSymbols[meanNeighbourSymbol]
    indexOfFirstAtomOfNeighbourType=GetListOfElementIndicesFromStructure(meanNeighbourSymbol, structCopy)[0]
    meanNeighbourNewSymbol = structCopy[meanNeighbourIndex]
    if(meanNeighbourIndex!=indexOfFirstAtomOfNeighbourType-1): #in other words, don't swap positions if the top of the element list is next after the neighbour - in other other words, the neighbour is already at the top of its respective list
        structCopy[meanNeighbourIndex], structCopy[indexOfFirstAtomOfNeighbourType]=structCopy[indexOfFirstAtomOfNeighbourType],structCopy[meanNeighbourIndex]
    
    Poscar(structCopy).write_file(f"YAGCe_{proxOrDistTag}_{meanNeighbourSymbol}.vasp", significant_figures=16)

    FindAndReplace(f"YAGCe_{proxOrDistTag}_{meanNeighbourSymbol}.vasp", "Og", meanNeighbourSymbol)

print()
print("Success!")