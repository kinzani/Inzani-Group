#!/usr/bin/env python3
from megnet.models import MEGNetModel
from pymatgen.core.structure import Structure
import os
from pymatgen.ext.matproj import MPRester
import argparse

#For more information on how to use these machine learning tools and other related tools, check out the GitHub repo for MEGNet: https://github.com/materialsvirtuallab/megnet#limitations

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
                    print("API key is valid. Saving API key to file: APIkey.txt")
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


def FormationEpredictor(poscarFileName="POSCAR", materialID=None):
    """
    Using the 2019 MP formation energy model from MEGNet.
    This function takes either a POSCAR (relative) path or a Materials Project ID, which can be specified by the poscarFileName and materialID parameters respectively.
    By default, poscarFileName is set to 'POSCAR', so if your POSCAR doesn't have a special name, you can just call this function without any inputs.
    For an official example of how to predict formation energy with the 2019 MP formation energy model, visit: https://github.com/materialsvirtuallab/megnet/blob/master/notebooks/Property%20Prediction%20with%20Pre-built%20MEGNet%20models.ipynb
    """

    model = MEGNetModel.from_file('mvl_models/mp-2019.4.1/formation_energy.hdf5')
    if(materialID!=None):
        APIkey = APIkeyChecker()
        mpr = MPRester(APIkey)
        struct = mpr.get_structure_by_material_id(materialID)
    else:
        struct = Structure.from_file(poscarFileName)
    prediction = model.predict_structure(struct).ravel()[0] #ravel() is a numpy array method that converts a multi-dimensional array into a 1D, contiguous array. Ngl, you don't need to use the ravel() method - you can just do [0] and get out the prediction (assuming there is just one).
    print("\n"*9) #done to separate out the tensorflow warning messages from the output of this script.
    print(f"Predicted formation energy: {prediction:.3f} eV/atom")

parser = argparse.ArgumentParser(prog = 'Formation energy predictor using MEGNet.',
                    epilog = 'Be sure to check out the MEGNet GitHub repo https://github.com/materialsvirtuallab/megnet')
parser.add_argument('-f', '--file', type=str, default="POSCAR", help="(Relative) Path to the POSCAR file used for the prediction. By default, this program will look for a POSCAR in your current working directory.")
parser.add_argument("-i", "--id", type=str, default=None, help="Materials project ID used to acquire a structure used for prediction. If this parameter is supplied, the 'file' parameter.")


args = parser.parse_args()


FormationEpredictor(poscarFileName=args.file, materialID=args.id)