from json_tricks import dumps, loads #the json module doesn't support non-standard types (such as the output from MAPI),
                                     #but json_tricks does

def SaveDictAsJSON(fileName, dictionary, indent=4):
    with open(fileName+".json", "w") as f:
        f.write(dumps(dictionary, indent=indent)) #don't need to read this since it's just a 'checkpoint'

def ReadJSONFile(fileName):
    with open(fileName+".json", "r") as f:
        return loads(f.read()) #loads() returns the string from f.read() as dict
