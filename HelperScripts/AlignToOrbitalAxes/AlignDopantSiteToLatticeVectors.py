#!/usr/bin/env python3

from pymatgen.analysis.local_env import CrystalNN
from pymatgen.core.structure import Structure, Molecule
import numpy as np
from pymatgen.core.composition import Composition
import math
import argparse
import os
import shutil
import sys, os

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
    print(f"Principal moments of inertia: {principal_moi}")
    principal_axes = [principal_axes_mat[:, i] for i in range(3)] #transpose the matrix - for reasons beyond my understanding, the eigenvectors seem to come in colummn form, so for python to be able to use an eigenvector, you need to make the column vectors into row vectors (why this isn't done by default is beyond me)
    
    return principal_moi, principal_axes


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
    cartCoords = [site.coords for site in sites]
    siteComplex = Molecule(elements, cartCoords) #if only I could put quotes in variable names...(for future me, this is not legitimate complex that's being made - that's the joke)
    return siteComplex



def countdigits(N):
    count = 0;
    while (N):
        count = count + 1;
        N = int(math.floor(N / 10));
    return count;
     
# Function to generate
# all cyclic permutations
# of a number
def cyclic(N):
    num = N;
    n = countdigits(N);
    cyclicPermutations = []
    while (1):
        cyclicPermutations.append(int(num))
         
        # Following three lines
        # generates a circular
        # permutation of a number.
        rem = num % 10;
        div = math.floor(num / 10);
        num = ((math.pow(10, n - 1)) *
                           rem + div);
         
        # If all the permutations
        # are checked and we obtain
        # original number exit from loop.
        if (num == N):
            break;
    
    cyclicPermutations = [list(str(x)) for x in cyclicPermutations]
    cyclicPermutations = np.array([np.array([int(x) for x in nums])-1 for nums in cyclicPermutations])
    return cyclicPermutations


def GetRotatedLatticeParams(molecule, latticeParams):
    cyclicPermutations = cyclic(123)
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
    print(f"Principal moments of inertia: {principal_moi}")
    rotatedLatticeParams = principal_axes_mat@latticeParams #principal axes are column vectors, and lattice params are row vectors
    largestEigValLatticeParams = np.array([rotatedLatticeParams[:,x] for x in cyclicPermutations[0]]).T
    middleEigValLatticeParams = np.array([rotatedLatticeParams[:,x] for x in cyclicPermutations[1]]).T
    smallestEigValLatticeParams = np.array([rotatedLatticeParams[:,x] for x in cyclicPermutations[2]]).T


    return largestEigValLatticeParams, middleEigValLatticeParams, smallestEigValLatticeParams


def GetNumbersOfAtomsPerElement(formula):
    return dict(Composition(formula).as_dict())

def FindDopantSiteIndex(structure):

    """Finds the atom index of an extrinsic defect by analysing ratios of atoms in the structure formula

    Args:
        structure (pymatgen.Structure): A Pymatgen Structure object that contains the extrinsic defect.

    Returns:
        dopantSiteIndex (int): The 0-indexed atom index of the extrinsic defect.
    """

    comp = GetNumbersOfAtomsPerElement(structure.formula)
    potentialDopantList=list({k:v for (k,v) in comp.items() if v==1}.keys())
    if(len(potentialDopantList)==1):
        dopantIdentity = potentialDopantList[0]
        print(f"Dopant appears to be {dopantIdentity}.")
        dopantSiteIndex = next(structure.index(site) for site in structure if site.species_string == dopantIdentity)
        return dopantSiteIndex
    else:
        print("You might not have a dopant present.")

def GetDopantSiteComplex(structure):
    """Acquires the dopant site complex from a doped cell.

    Args:
        structure (pymatgen.Structure): A Pymatgen Structure object that contains the extrinsic defect.

    Returns:
        dopantSiteComplex (Molecule): A Pymatgen Molecule object that contains the extrinsic defect and its neighbouring atoms.
    """
    dopantSiteIndex = FindDopantSiteIndex(structure) #acquires the index of the extrinsic defect.
    dopantSiteComplex = GetComplexFromSiteInStruct(structure, dopantSiteIndex)
    return dopantSiteComplex


def GetLatticeParams(pocscar_filename):
    with open(pocscar_filename, 'r', encoding='utf-8') as file:
        data = file.readlines()
    latticeParams = data[2:5]
    latticeParams = np.array([np.array([float(x) for x in vector.strip().split()]) for vector in latticeParams])
    return latticeParams

def WriteNewLatticeParamsPOSCAR(initial_pocscar_filename, final_poscar_filename, newLatticeParams):
    with open(initial_pocscar_filename, 'r', encoding='utf-8') as file:
        data = file.readlines()
    formattedNewLatticeParams = [f"{latParam[0]:.16f} {latParam[1]:.16f} {latParam[2]:.16f}\n" for latParam in newLatticeParams]
    data[2:5] = formattedNewLatticeParams
    with open(final_poscar_filename, 'w', encoding='utf-8') as file:
        file.writelines(data)

def MakeXYZfileOfDopantComplex(structCoordFileName, xyzFilename, dopant_index):
    structure = Structure.from_file(structCoordFileName)
    dopantComplex=GetComplexFromSiteInStruct(structure, dopant_index)
    coords = [site.coords for site in dopantComplex]
    elements = [site.species_string for site in dopantComplex]
    numOfAtoms = len(elements)
    startOfFile = [f"{numOfAtoms}\n\n"]
    restOfFile = [f"{elem} {coord[0]} {coord[1]} {coord[2]}\n" for (elem, coord) in list(zip(elements, coords))]
    fileContents = startOfFile+restOfFile
    with open(f"{xyzFilename}.xyz", 'w', encoding='utf-8') as file:
        file.writelines(fileContents)


def main():
    parser = argparse.ArgumentParser(
                        prog='Symmetry Aligner',
                        description='Aligns the lattice vectors to the principal axes of a given defect atom.')

    parser.add_argument('-f', '--file', type=str, help="Structure filename (VASP POSCAR format).")
    parser.add_argument('-i', '--index', type=int, help="Index of defect atom (0-indexed). This is the index as seen in VESTA minus 1.")
    args = parser.parse_args()

    coords_file = args.file
    print(f"Reading in structure from {coords_file}.")
    struct = Structure.from_file(coords_file)

    print("Acquiring dopant site complex.")
    dopantSiteComplex=GetComplexFromSiteInStruct(struct, args.index)
    latticeParams = GetLatticeParams(coords_file)
    print("Acquiring aligned lattice parameters.")
    largestEigValLatticeParams, middleEigValLatticeParams, smallestEigValLatticeParams = GetRotatedLatticeParams(dopantSiteComplex, latticeParams)


    formula = struct.formula.replace(" ", "")
    if(not os.path.isdir(formula)): # make directory if it doesn't already exist and save files inside
        print("Saving structure files.")
        os.mkdir(formula)
        shutil.copy(coords_file, formula)
        os.chdir(formula)
        WriteNewLatticeParamsPOSCAR(coords_file, f"{formula}_largestEigVal.vasp", largestEigValLatticeParams)
        MakeXYZfileOfDopantComplex(f"{formula}_largestEigVal.vasp", "largestEigValComplex", args.index)
        WriteNewLatticeParamsPOSCAR(coords_file, f"{formula}_middleEigVal.vasp", middleEigValLatticeParams)
        MakeXYZfileOfDopantComplex(f"{formula}_middleEigVal.vasp", "middleEigValComplex", args.index)
        WriteNewLatticeParamsPOSCAR(coords_file, f"{formula}_smallestEigVal.vasp", smallestEigValLatticeParams)
        MakeXYZfileOfDopantComplex(f"{formula}_smallestEigVal.vasp", "smallestEigValComplex", args.index)
        os.chdir("..")
    else:
        print(f"{formula} directory already exists!")


main()