import os

cwd = os.getcwd().split("/")[-2]
Uval = cwd.replace("U_", "")
print(Uval)
