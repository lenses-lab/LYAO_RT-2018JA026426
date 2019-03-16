## This is the working directory for LYAO_RT.

### LYAO_RT is only known to run in a Unix environment.

LYAO_RT takes in observation conditions and a model thermosphere (including H, N2, and O2) to output calculated Hydrogen density, temperature, and column density through exospheric altitudes. See Bishop (1999) for an explanation of the code.

This particular executable runs NRLMSISE-00 as the model thermosphere. MSIS is already included in the executable.

#### This command will run the entire RT code once:
```
./testscript
```

#### The executables that will run in series when ```testscript``` is called are ```test_rt``` and ```test_los```.

#### When ```test_rt``` is run, it completes the following tasks:

* Interprets ```infile.dat``` for information on observing conditions and what type of calculation to use when extending the thermospheric model to the exosphere
* Runs MSIS based on inputs to get initial thermospheric model
* Run exospheric extension on the thermospheric model based on inputs
* Writes MSIS output and exospheric extension output to a file called ```H_alpha.source```

#### When ```test_los``` is run, it completes the following tasks

* Interprets ```inputs_los.dat``` for pointing information
* Runs a line-of-sight integration calcuation based on pointing information and test_rt output to get H-alpha emission intensity along line-of-sight
* Writes line-of-sight intensity output to a file called ```hab_los.dat``` and a simplified file called ```formatted.source```

#### To avoid clutter, it is recommended that users of LYAO_RT not save personal copies of the input and output files in this directory. 

### See the ```LYAO_RT python code directory``` for scripts to run this code over many observing conditions, parse the output, and make plots.
