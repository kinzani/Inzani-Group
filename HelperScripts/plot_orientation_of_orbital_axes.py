#!/usr/bin/env python3

from pymatgen.analysis.local_env import CrystalNN
from pymatgen.core.structure import Structure, Molecule
import numpy as np
from pymatgen.core.composition import Composition
import math
import argparse
import os
from qutip import Bloch
import shutil
import sys, os
import matplotlib.pyplot as plt


# Disable printing
def BlockPrint():
    sys.stdout = open(os.devnull, 'w')
    sys.stderr = open(os.devnull, 'w')

# Restore printing
def EnablePrint():
    sys.stdout = sys.__stdout__

def GetMoIandPrincipalAxes(molecule):
    coords = [site.coords for site in molecule]
    weights = [float(site.species.weight) for site in molecule]
    atoms = list(zip(weights, coords))
    #acquiring the centre of mass
    com = np.zeros(3)
    m = 0.0
    for atom in atoms:
        com += atom[0] * atom[1]
        m += atom[0]
    com /= m

    moi_tensor = np.zeros((3, 3))
    identity = np.eye(3)

    for atom in atoms:
        rel_pos = atom[1] - com #centring on centre of mass (com)
        moi_tensor += atom[0] * (np.linalg.norm(rel_pos)**2 * identity - np.outer(rel_pos, rel_pos)) #this seems to be a sneaky way of making the inertia tensor in one go, rather than doing it element by element - check out the definition of the inertia tensor here https://en.wikipedia.org/wiki/Moment_of_inertia#Inertia_tensor
    principal_moi, principal_axes_mat = np.linalg.eigh(moi_tensor)
    # print(f"Principal moments of inertia: {principal_moi}")
    principal_axes = [principal_axes_mat[:, i] for i in range(3)] #transpose the matrix - for reasons beyond my understanding, the eigenvectors seem to come in colummn form, so for python to be able to use an eigenvector, you need to make the column vectors into row vectors (why this isn't done by default is beyond me)
    
    return principal_moi, principal_axes, com


def FindImage(site, struct):
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
    BlockPrint()
    sites=[site["site"] for site in CrystalNN().get_nn_info(struct, siteIndex)]
    EnablePrint()
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

def GetComplexFromSiteInStruct(struct, siteIndex):
    neighbourSites=list(ReturnNeighborIndices(struct, siteIndex).values())
    sites = neighbourSites+[struct[siteIndex]]
    elements = [site.specie for site in sites]
    cart_coords = [site.coords for site in sites]
    siteComplex = Molecule(elements, cart_coords) #if only I could put quotes in variable names...(for future me, this is not legitimate complex that's being made - that's the joke)
    return siteComplex



parser = argparse.ArgumentParser(
                    prog='Orbital axis plotter',
                    description='Obtains the principal axes of inertia (orbital axes) of a given site in a structure using the inertia tensor method.',
                    epilog='Slapped together by Dan Criveanu.')

parser.add_argument('-f', '--file', help="Structure file.", default="POSCAR")
parser.add_argument("-i", "--index", help="Site index (0-indexed). The default is -1, assuming the site of interest is at the end of the list of atoms.", default=-1)
args = parser.parse_args()

struct = Structure.from_file(args.file)
polyhedron = GetComplexFromSiteInStruct(struct, args.index)
_, principal_axes, com = GetMoIandPrincipalAxes(polyhedron)
# small_MoI_axis, medium_MoI_axis, large_MoI_axis = principal_axes


b = Bloch()
b.vector_color = ["#332288", "#117733", "#882255", "#332288", "#117733", "#882255"]
b.add_vectors(principal_axes)
b.add_vectors(-np.array(principal_axes))
b.zlabel = ['$z$', ""]

b.save("orbital_axes.png", dpin=300)
print("Orbital axis sphere image has been saved! :)")