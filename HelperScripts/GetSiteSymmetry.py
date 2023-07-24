#!/usr/bin/env python3

from pymatgen.analysis.local_env import BrunnerNN_real
from pymatgen.core.structure import Structure, Molecule
from pymatgen.symmetry.analyzer import PointGroupAnalyzer
import argparse

def FindImage(site, structure):
    """
    So, funny story - if you try to get the index of a neighbour of a site using the original structure you got the neighbours from,
    Python may scream at you, because the neighbour you have is an image of a site that's within the structure. This function finds
    the relevant image in the structure and returns that.
    
    site - neighbor object which you want to find the image of inside the structure it came from.
    structure - the structure you're analysing.
    """
    return next(image for image in struct if site.is_periodic_image(image)) #next() function acts like list comprehension, but only returns the first instance that matches the if statement given

def ReturnNeighborIndices(struct, siteIndex):
    """
    :struct - structure object
    :siteIndex - the index of the site of which you want to find neighbours of
    :distFromSite - the radius in Angstrom of which you're looking for neighbours around the site with index siteIndex
    """
    sites=[site["site"] for site in BrunnerNN_real(cutoff=12).get_nn_info(struct, siteIndex)]
    neighbourIndices={}
    for site in sites:
        try:
            neighbourIndex=struct.index(site)
        except ValueError:
            image=FindImage(site,struct)
            neighbourIndex=struct.index(image)
        #neighbourIndices.append(neighbourIndex)
        neighbourIndices[neighbourIndex]=site
    return neighbourIndices

def GetSiteSymmetry(struct, siteIndex):
    neighbourSites=list(ReturnNeighborIndices(struct, siteIndex).values())
    sites = neighbourSites+[struct[siteIndex]]
    elements = [site.specie for site in sites]
    cartCoords = [site.coords for site in sites]
    siteComplex = Molecule(elements, cartCoords) #if only I could put quotes in variable names...(for future me, this is not legitimate complex that's being made - that's the joke)
    sitePointGroup = PointGroupAnalyzer(siteComplex).get_pointgroup()
    print(f"Symmetry of {struct[siteIndex].species_string} site in {struct.formula}: {sitePointGroup}")
    return sitePointGroup

parser = argparse.ArgumentParser(prog = 'Site symmetry acquirer.',
                    description = 'Acquires the point group symmetry of a given site by its index (zero-indexed).',
                    epilog = 'Hope you have fun with this program :)')
parser.add_argument("-i", "--index", type=int, help="The index of the site whose symmetry will unveiled.")
parser.add_argument("-f", "--file", type=str, default="POSCAR", help="File that will be used to acquire structure. The default file is POSCAR.")
args = parser.parse_args()

struct = Structure.from_file(args.file)
GetSiteSymmetry(struct, args.index)


