#!/usr/bin/env python3

from pymatgen.core.structure import Structure, Molecule
from pymatgen.symmetry.analyzer import PointGroupAnalyzer
from pymatgen.analysis.local_env import MinimumDistanceNN
import argparse

def GetSiteSymmetry(struct, siteIndex, tolerance=0.3):
    mdd = MinimumDistanceNN()
    bonded_structure = mdd.get_bonded_structure(struct) #make StructureGraph object
    site_neighbours = bonded_structure.get_connected_sites(siteIndex) #get neighbours of the chosen site
    site_neighbours = [connected_site.site for connected_site in site_neighbours] #acquiring PeriodicSite objects from the ConnectedSite objects that .get_connected_sites returned
    site_polyhedron = site_neighbours+[struct[siteIndex]] #creating the site polyhedron -> neighbours+chosen site
    site_polyhedron = Molecule.from_sites(site_polyhedron) #creating a Molecule object from the site_polyhedron defined above
    sitePointGroup = PointGroupAnalyzer(site_polyhedron, tolerance).get_pointgroup()
    print(f"Symmetry of {struct[siteIndex].species_string} site in {struct.formula}: {sitePointGroup}")
    return sitePointGroup


parser = argparse.ArgumentParser(prog = 'Site symmetry acquirer.',
                    description = 'Acquires the point group symmetry of a given site by its index (zero-indexed).',
                    epilog = 'Hope you have fun with this program :)')
parser.add_argument("-i", "--index", type=int, help="The index of the site whose symmetry will unveiled.")
parser.add_argument("-f", "--file", type=str, default="POSCAR", help="File that will be used to acquire structure. The default file is POSCAR.")
parser.add_argument("-t", "--tol", type=float, default=0.3, help="The tolerance for deriving the symmetry of a site. The default value is 0.3.")
args = parser.parse_args()

struct = Structure.from_file(args.file)
GetSiteSymmetry(struct, args.index, args.tol)


