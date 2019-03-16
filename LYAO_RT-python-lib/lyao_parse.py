##	Parser for LYAO_RT output
#	Margaret Gallant
#	Last Updated: 04-10-2018
#
## How to Use this Class:
#  From within python script or command line, run LYAO_RT("savedir")
#  where "savedir" includes only one of each of these three files:
#  1) infile.dat or inputs.rt
#  2) H_alpha.source
#  3) hab_los.dat
#  
## Example
#  from lyao_run import *
#  import matplotlib.pyplot as plt
#
#  run = LYAO_RT("saved_run")
#  print(run.inf.info)
#  plot(run.src.z,run.src.H)
#
## Parameters that are parsed:
#	__.inf			--	infile parameters
#	__.inf.info		--  a string containing the infile, useful for display
#	__.inf.loc		--	[lat, lon]
#	__.inf.time		--	[DOY, YY, Hr]
#	__.inf.ap		--	[apflag, average_Ap, 3-hr Ap x 5]
#	__.inf.f107		--	[f107daily, f107averaged]
#	__.inf.msis		--	MSIS flag (int)
#	__.inf.exo		--	Exobase density
#	__.inf.flux		--	Vertical Transport Flux
#	__.inf.peak		--	Mesopause Peak Density
#	__.inf.igeo		--	IGEO Exosphere flag (int)
#	__.inf.satt		--	Satellite Temperature
#	__.inf.satd		--	Satellite Density
#
#	__.src			--	source file parameters
#   __.src.msis_input	--	MSIS inputs [lat,lon,DOY,year,UT,STL,Ap,f10.7]
#	__.src.msis_z	--	MSIS surface altitude (km)
#	__.src.msis_r	--	MSIS radial altitude (km)
#	__.src.msis_T	--	MSIS Temperature (K)
#	__.src.msis_H	--	MSIS Hydrogen Density
#	__.src.msis_O2	--	MSIS Molecular Oxygen Density
#	__.src.cd_H		--	Hydrogen Column Density
#	__.src.cd_O2	--	Molecular Oxygen Column Density
#	__.src.cd_tot	--	Total Column Density, cd_H + cd_O2 with opacity scale
#	__.src.cd_exo	--	Column Density above Exobase
#	__.src.z		--	IGEO-extended altitudes
#	__.src.H		--	IGEO-extended Hydrogen Density
#	__.src.O2		--	IGEO-extended Molecular Oxygen Density
#	__.src.T		--	IGEO-extended Temperature
#
#	__.los			--	los file parameters
#	__.los.Ha_int	--	H-alpha emission intensity
#	__.los.shdalt	--	Shadow Altitude

import os, sys
import numpy as np
from matplotlib import pyplot as plt

class Infile:
	def __init__(self, infile_filepath):
		## Open infile.dat file
		id = open(infile_filepath)
		lines = id.readlines()
		
		## Inputs.rt text box string
		id.seek(0,0)
		info = id.read()
		id.close()
		self.info = 'inputs.rt\n'+info[:-1]
		
		## Read Lyman Series
		self.ly = int(lines[0].split()[0])
		
		## Read location [lat, lon]
		self.loc = [float(i) for i in lines[1].split()]
		
		## Read time [DOY, YY, HH.ff]
		self.time = [int(float(i)) for i in lines[2].split()]+[float(lines[3].split()[0])]
		
		## Read Ap Indices [flag, average_Ap, 4hour_Ap]
		ap = [float(i) for i in lines[4].split()]
		ap[0] = int(ap[0])
		self.ap = ap
		
		## Read f10.7 [Daily, Averaged]
		self.f107 = [float(i) for i in lines[5].split()]
		
		## Read MSIS Flag
		self.msis = int(lines[6].split()[0])
		
		## Read Hydrogen Density parameters
		self.exo = float(lines[6].split()[1])
		self.flux = float(lines[6].split()[2])
		self.peak = float(lines[6].split()[3])
		
		## Read IGEO flag
		self.igeo = int(lines[7].split()[0])
		
		## Read Satellite Population parameters
		self.satt = float(lines[7].split()[1])
		self.satd = float(lines[7].split()[2])

class Source:
	def __init__(self,source_filepath):
		Re = 637100000
		## Open H_alpha.source file
		id = open(source_filepath)
		lines = id.readlines()
		id.close()
		
		self.msis_input = lines[1].split()[:8]
		
		for i,line in enumerate(lines):
			if "MSIS" in line:
				msis_start = i+2
			if "EXOSPHERE & OPTICAL QUANTITIES" in line:
				msis_end = i-1
			if "COLUMN DENSITIES" in line:
				cd_start = i+1
			if "NOMINAL CENTROID RADII" in line:
				z_start = i+1
			if "HYDROGEN DENSITIES" in line:
				h_start = i+1
			if "MOLECULAR OXYGEN DENSITIES" in line:
				o_start = i+1
			if "TEMPERATURES" in line:
				t_start = i+1
		
		## Read MSIS grid, lines 4-65
		msis = []
		for line in lines[msis_start:msis_end+1]:
			msis.append([float(i) for i in line.split()])
		self.msis_z = [msis[i][0] for i in range(len(msis))]
		self.msis_r = [msis[i][1] for i in range(len(msis))]
		self.msis_T = [msis[i][2] for i in range(len(msis))]
		self.msis_H = [msis[i][3] for i in range(len(msis))]
		self.msis_O2 = [msis[i][4] for i in range(len(msis))]
		
		## Read Column Densities, line 69
		## Order: colmd_H, colmd_O2, colmd_tot, colmd_exo
		self.cd_H = float(lines[cd_start].split()[0])
		self.cd_O2 = float(lines[cd_start].split()[1])
		self.cd_tot = float(lines[cd_start].split()[2])
		self.cd_exo = float(lines[cd_start].split()[3])
		
		## Read Zone Densities and Temperatures
		## Hydrogen Densities, lines 85-87
		## O2 Densities, lines 89-91
		## Temps, lines 93-95
		z = [float(i) for i in lines[z_start].split()]+[float(i) for i in lines[z_start+1].split()]+[float(i) for i in lines[z_start+2].split()]
		self.z = [(i-Re)/10**5 for i in z]
		self.H = [float(i) for i in lines[h_start].split()]+[float(i) for i in lines[h_start+1].split()]+[float(i) for i in lines[h_start+2].split()]
		self.O2 = [float(i) for i in lines[o_start].split()]+[float(i) for i in lines[o_start+1].split()]+[float(i) for i in lines[o_start+2].split()]
		self.T = [float(i) for i in lines[t_start].split()]+[float(i) for i in lines[t_start+1].split()]+[float(i) for i in lines[t_start+2].split()]
				 
class Los:
	def __init__(self,hablos_filepath):
		## Open hab_los.dat file
		id = open(hablos_filepath)
		lines = id.readlines()
		id.close()
		
		## Read Shadow Altitude
		SA = [round(float(line.split()[3]), 6) for line in lines[1:len(lines)]]
		
		## Read Emission Intensities
		Ha = [float(line.split()[4]) for line in lines[1:len(lines)]]
		
		## Sort by Shadow Altitude in Ascending Order
		sorted_los = list(zip(*sorted(zip(SA,Ha),key=lambda x: x[0])))
		
		## Assign LOS attributes
		self.shdalt = sorted_los[0]
		self.Ha_int = sorted_los[1]
		
class LYAO_RT:	
	def __init__(self,savedir):
		flag = 0
		for dp,dn,fn in os.walk(os.path.normpath(savedir)):
			for file in fn:
				if "hab_los" in file:
					hablos_filepath = dp+"/"+file
					flag = flag + 1
				if "alpha" in file:
					source_filepath = dp+"/"+file
					flag = flag + 1
				if ("infile" in file) or ("inputs.rt" in file):
					infile_filepath = dp+"/"+file
					flag = flag + 1
		if flag < 3:
			print('\nError: Save Directory does not include all three files.')
			sys.exit()
		else:
			self.inf = Infile(infile_filepath)
			self.src = Source(source_filepath)
			self.los = Los(hablos_filepath)

def IntCSS(ax,title=r"H-$\alpha$ Emission Intensity"):
	ax.set_yscale('linear')
	ax.set_xscale('linear')
	ax.set_title(title)
	ax.set_ylabel("Intensity (R)")
	ax.set_xlabel("Shadow Altitude (km)")

def HDensCSS(ax,title="Hydrogen Density Profile"):
	ax.set_yscale('log')
	ax.set_xscale('log')
	ax.set_title(title)
	ax.set_ylabel("Altitude (km)")
	ax.set_xlabel(r"[H] (cm$^{-3}$)")