import glob

stepVal = 0.5

dirs = glob.glob("SR*")


dirs = [directory.replace("SR", "") for directory in dirs]
dirs.sort()
latestVal = float(dirs[-1])
latestDirName = f"SR{latestVal}"

print(latestDirName)
