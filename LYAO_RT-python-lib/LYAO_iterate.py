# Iterator for PBO LYAO_RT runs
# Author: Margaret Gallant

### IMPORT MODULES ###
import os, sys, shutil, subprocess
from datetime import datetime
import numpy as np
import pandas as pd
import re
from LYAO_inputsbuilder import *

# Set-up Shadow Inputs
yr,dst = 2000, np.linspace(93,303,303-93+1)
observer = "pbo"
UTCoffset = 6
UTCdst = UTCoffset - 1
tms = [11,4] # AM,PM in UT
dates = [datetime.strptime("%i %i"%(yr,x),"%Y %j") for x in range(1,367)]

# Set up Paths
path = os.path.abspath(os.path.dirname(sys.argv[0]))+"/"
LYAOpath = path+'../LYAO_RT/'
USNOpath = path+'../USNO/%s-%i-Nautical-Twilight-USNO.txt'%(observer.upper(),yr)
USNOdf = USNOparser(USNOpath)
savedir = path+'../PBO_finegrid/'

# Set-up MSIS inputs
f107s = np.linspace(50,270,12)
#f107s = [70]
Aps=np.linspace(5,95,10)
Ap=5

run_count=0

for date in dates:
	doy = date.strftime("%-j")
	UTCoffset = UTCdst if int(doy) in dst else UTCoffset
		
	# Get Shadow Time Intervals
	dawn,dusk,midnight = dt2tod(date,USNOdf,UTCoffset)
	tm_int = 10  # Interval in minutes
	AMtime = [midnight,dawn,tm_int]
	PMtime = [dusk,midnight,tm_int]
	
	# Calculate Time Of Day for AM & PM cases
	tmdt = [date.replace(hour=tms[0]),date.replace(hour=tms[1])]
	
	for f107 in f107s:
			for tm,dt,tmint in zip(["AM","PM"],tmdt,[AMtime,PMtime]):
				print(tmint)

				# Create Save Directory for Each Run
				tmpath = savedir+"DOY_%s/f107_%i/%s"%(doy,f107,tm)
				if not os.path.exists(tmpath):
					os.makedirs(tmpath)

				# Run Shadow Code
				shdwdf = shadow(observer,tmint,shdpath=path+'../Shadow/')
	
				# Create LOS input file
				shd2los(shdwdf,LYAOpath+'inputs_los.dat')

				# Create a file prefix for save directory
				fprfx = 'doy-%s_%s_f107-%i_'%(doy,tm,f107)
		
				#Save LOS inputs copy to AM & PM output directories
				shutil.copyfile('%s/inputs_los.dat'%LYAOpath, '%s/%sinputs_los.dat'%(tmpath,fprfx))	

				# Write RT input file
				RT = RTinputstr(observer,dt,f107,Ap)
				writeRTinput(LYAOpath,RT)
				shutil.copyfile('%s/infile.dat'%LYAOpath, '%s/%sinfile.dat'%(tmpath,fprfx))
				print("---- Begin Run: %s ----"%fprfx[:-1])

				# Run LYAO_RT
				subprocess.run(args=["./testscript"], shell=True, cwd=LYAOpath)

				# Save output
				shutil.copyfile("%s/H_alpha.source"%LYAOpath, "%s/%sH_alpha.source"%(tmpath,fprfx))
				shutil.copyfile("%s/hab_los.dat"%LYAOpath, "%s/%shab_los.dat"%(tmpath,fprfx))
	
				run_count = run_count + 1
				print("---- Run Saved to %s ----"%tmpath)
				print("---- Number of Runs So Far: %i ----\n"%run_count)
