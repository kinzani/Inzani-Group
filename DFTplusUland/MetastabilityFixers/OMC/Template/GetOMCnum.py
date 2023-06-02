import os

cwd = os.getcwd().split("/").pop()
OMCnum = cwd.replace("OMC", "")
print(OMCnum)
