#!/usr/bin/env python3
from megnet.models import MEGNetModel
import numpy as np
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


def BandGapPredictor(poscarFileName="POSCAR", materialID=None):
    """
    Using MEGNet's multi-fidelity graph network models for band gaps.
    This function takes either a POSCAR (relative) path or a Materials Project ID, which can be specified by the poscarFileName and materialID parameters respectively.
    By default, poscarFileName is set to 'POSCAR', so if your POSCAR doesn't have a special name, you can just call this function without any inputs.
    """

    all_models = [MEGNetModel.from_file('mvl_models/mf_2020/pbe_gllb_hse_exp/%d/best_model.hdf5' % i) for i in range(6)]
    if(materialID!=None):
        APIkey = APIkeyChecker()
        mpr = MPRester(APIkey)
        struct = mpr.get_structure_by_material_id(materialID)
    else:
        struct = Structure.from_file(poscarFileName)
    struct.state = [3] #The fidelity level is provided via structure.state, where 0, 1, 2, 3 correspond to PBE, GLLB-SC, HSE and Experiment, respectively.
    predictions = [model.predict_structure(struct) for model in all_models]
    predictions1array=np.concatenate(predictions)
    print("\n"*9) #done to separate out the tensorflow warning messages from the output of this script.
    print(f"Predictions from each model: {predictions1array}")
    print(f"(Average) Predicted band gap: {np.mean(predictions1array):.2f} eV")

parser = argparse.ArgumentParser(prog = "Band gap predictor using MEGNet's multi-fidelity graph network models for band gaps.",
                    epilog = 'Be sure to check out the MEGNet GitHub repo https://github.com/materialsvirtuallab/megnet')
parser.add_argument('-f', '--file', type=str, default="POSCAR", help="(Relative) Path to the POSCAR file used for the prediction. By default, this program will look for a POSCAR in your current working directory.")
parser.add_argument("-i", "--id", type=str, default=None, help="Materials project ID used to acquire a structure used for prediction. If this parameter is supplied, the 'file' parameter.")


args = parser.parse_args()


BandGapPredictor(poscarFileName=args.file, materialID=args.id)