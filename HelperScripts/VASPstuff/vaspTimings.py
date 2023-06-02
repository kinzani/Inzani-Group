#!/usr/bin/env python3
import numpy as np
import datetime
import os

os.system("grep LOOP+ OUTCAR | awk '{print $7}' > realTimes")
times=np.loadtxt("realTimes")
overallTime=round(np.sum(times))
overallTimeStr=str(datetime.timedelta(seconds=overallTime))
print(f"Time taken (h:m:s): {overallTimeStr}")
