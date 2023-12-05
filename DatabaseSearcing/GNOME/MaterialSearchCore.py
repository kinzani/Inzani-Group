import numpy as np
import os
import pandas as pd
from Filters import Analysis
from Util import get_NElems, TurnElementsIntoList





def MaterialSearch(searchName, orderOfFilters):
    if(not os.path.isdir(searchName)):
        print(f"Creating search directory {searchName} and reading in GNOME database.")
        if(os.path.isfile("gnome_data_stable_materials_summary.csv")): #new version of the database has a different name than before, so I'm just renaming it to what it used to be lol
            os.rename("gnome_data_stable_materials_summary.csv", "stable_materials_summary.csv")

        results = pd.read_csv("stable_materials_summary.csv") #loading database information
        os.mkdir(searchName)
        os.chdir(searchName)

        initialFilterName = "Database"
        initialSearchFilename = f"0_{initialFilterName}"
        if(not os.path.isfile(f"{initialSearchFilename}.json")):
            results['Elements'] = results['Elements'].apply(TurnElementsIntoList)
            NElements = results['Elements'].apply(get_NElems)
            results.insert(loc = 5,
                            column = 'NElements',
                            value = NElements)
            results = results.replace([np.inf, -np.inf, np.nan], None) #replace infinite values and NaN with "None"
            results.to_json(f"{initialSearchFilename}.json", orient="records", indent=4)

            #logging
            with open("SearchLog.txt", mode="w") as f:
                f.write(f"{initialFilterName}: {len(results.index)}\n")
            print("Gnome database has been prepped for further analysis.")
    else:
        print(f"Search directory {searchName} already exists.")
        os.chdir(searchName)


    Analysis(searchName, orderOfFilters)
    os.chdir("..")