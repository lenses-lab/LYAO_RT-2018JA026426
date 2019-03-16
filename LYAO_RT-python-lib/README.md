## This repository holds several python classes and scripts that are useful for running LYAO_RT and parsing its output.

These files should be used in the following order.

### 1) LYAO_inputsbuilder.py
This is a python class that includes several useful functions for building the inputs for an LYAO_RT run.

**Example**
```
from LYAO_inputsbuilder import *

## Set-up Shadow Inputs
observer = "pbo"
date = datetime.utcnow()
time = dt2shd(date)

## Run Shadow Code
shadow_dataframe = shadow(observer,time,shdpath=path_to_shadow)

## Create LYAO input file
shd2los(shadow_dataframe,"inputs_los.dat")

## Write RT infile.dat
RT = RTinputstr(observer,date,f107,Ap)
writeRTinput(path_to_LYAO,RT)

# Run LYAO_RT
subprocess.run(args=["./testscript"], shell=True, cwd=path_to_LYAO)
```

### 2) LYAO_iterate.py
This is fairly advanced example of how to use LYAO_inputsbuilder.py. It iterates over several f10.7 numbers, and over all 366 days of the year. This will take hours to run unless you change these parameters. It also assumes that your paths are set up as in this directory.

### 3) lyao_parse.py
This is a python class that interprets the input and output files to a particular LYAO_RT run. From within python script or command line, run ```LYAO_RT("savedir")``` where "savedir" includes only one of each of these three files:
1) infile.dat
2) H_alpha.source
3) hab_los.dat
 
**Example**
```
from lyao_parse import *
import matplotlib.pyplot as plt

run = LYAO_RT("saved_run")
print(run.inf.info)
plot(run.src.z,run.src.H)
```

### 4) lyao_colormap_plotter.py
This is a fairly advanced example of how to use lyao_parse.py to make a colormap of H alpha intensity over day of year and shadow altitude for both solar minimum(f10.7=70) and solar maximum(f10.7=210). To run this, you'll need to run LYAO_iterate.py for f10.7=70 and f10.7=210 over the entire year. Otherwise, edit this script to match whatever iterations you have run.
