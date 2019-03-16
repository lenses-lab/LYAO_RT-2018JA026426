####################################################################################################
# LYAO Inputs Builder
# Contains functions for running & parsing shadow code and 
# 	creating an LYAO LOS input file from shadow output
# Contains functions for parsing a USNO sunset/sunrise calendar
# Contains functions for writing LYAO RT input file
####################################################################################################
# Author: Margaret Gallant
# Written for Python v3.6
# Dependencies: shadow.exe (Jeff Percival, UW-Mad), LYAO driver file (Susan Nossal, UW-Mad), 
# 	LYAO_RT (James Bishop)
# Outstanding Python Modules: datetime, pandas
# Last Updated: 06-01-2018
####################################################################################################
# HOW TO USE:
# 
# from ShadowParser import *
#
# ## Set-up Shadow Inputs
# observer = "pbo"
# time = dt2shd(datetime.utcnow())
#
# ## Run Shadow Code
# shadow_dataframe = shadow(observer,time)
#
# ## Create LYAO input file
# shd2los(shadow_dataframe,"inputs_los.dat")
#
####################################################################################################
# BEGIN CODE 
####################################################################################################

### IMPORT MODULES ###
import os, sys, subprocess
from datetime import datetime
from calendar import isleap
import pandas as pd
import re

####################################################################################################
## Run the Shadow Code, Parse the Output, and Returns Shadow DataFrame
#  Not dependent on LYAO driver

def shadow(loc,time,radec=None,hadec=None,azel=None,shdpath='./Shadow/'):
	## run 'shadow.x86_64 -help' for more help
	## Check for location inputs
	#  Valid presets include: pbo, wiyn, or erau
	#  Otherwise, loc = (latitude, longitude, altitude) in format "[hr/dg] [mn] [sec]"
	if loc in ['pbo','kpno','wiyn','erau','ctio']:
		if loc=="kpno":
			locstr="-wiyn"
		elif loc=='ctio':
			locstr='-lon -70 47 56.4 -lat -30 42 46.8 -alt 2200'
		else:
			locstr = "-%s"%(loc)
	elif len(loc) == 3:
		locstr = "-lon %s -lat %s -alt %s"%(loc[0],loc[1],loc[2])

	
	## Check for time inputs
	#  Time inputs must be in UTC & formatted "YYYY MM DD HH MM SS.SSS"
	#  Valid time modes include single time and interval time
	#  Single time: time = "YYYY MM DD HH MM SS.SSS"
	#  Interval time: time = (start_time, end_time, time_interval)
	#    where time_interval is in integer minutes
	if len(time) == 3:
		tmstr = "-from %s -to %s -dt %i"%(time[0],time[1],time[2])
	elif len(time) == 1:
		tmstr = "-utc %s"%(time)
	else:
		tmstr = ""
	
	## Check for RA/Dec
	radecstr = "-ra %.3f -dec %.3f"%(radec[0],radec[1]) if radec != None else ""
	
	## Check for HA/Dec
	hadecstr = "-ha %.3f -dec %.3f"%(hadec[0],hadec[1]) if hadec != None else ""
	
	## Check for Az/El
	azelstr = "-az %.3f -el %.3f"%(azel[0],azel[1]) if azel != None else ""
	
	## Run Shadow Code
	command = "%sshadow %s %s %s %s %s > %soutput.txt"%(shdpath,locstr,tmstr,radecstr,hadecstr,azelstr,shdpath)
	print(command)
	subprocess.run(args=[command], shell=True)
	id = open(shdpath+"output.txt")
	lines = id.readlines()
	#line = id.read()
	id.close()
	
	df = pd.DataFrame()
	for line in lines:
		s = pd.Series(shdparser(line))
		df = df.append(s,ignore_index=True)
	return df

####################################################################################################
## Parse the Shadow output
#  Not dependent on LYAO driver

def shdparser(line):

	# Convert three dictionary keys in dms to one dictionary key in deg
	def convert2dec(dict,keys):
		dms = [dict[keys[0]],dict[keys[1]],dict[keys[2]]]
		del(dict[keys[0]],dict[keys[1]],dict[keys[2]])
		return float(dms[0]) + float(dms[1])/60 + float(dms[2])/(60*60)
	
	# Given a pattern, convert a string into a dictionary
	def string_to_dict(string, pattern):
		## string_to_dict Written by Dan H. on StackOverflow
		## https://stackoverflow.com/questions/11844986/
		## convert-or-unformat-a-string-to-variables-like-format-but-in-reverse-in-p
		regex = re.sub(r'{(.+?)}', r'(?P<_\1>.+)', pattern)
		matches = re.search(regex,string)
		values = list(matches.groups())
		keys = re.findall(r'{(.+?)}', pattern)
		_dict = dict(zip(keys, values))
		return _dict
	
	# Shadow output pattern
	pattern = 'ra/dec {ra_h}H {ra_m}M {ra_s}S {dec_d}D {dec_m}\' {dec_s}" shadow distance {shddist} km altitude {shdalt} km targ az {targaz} zd {targzd} sun az {sunaz} zd {sunzd} diff-az {diffaz} utc {utc} last {last_h}H {last_m}M {last_s}S vlsr {vlsr} km/s l/b {glon_h}H {glon_m}M {glon_s}S {glat_d}D {glat_m}\' {glat_s}" ha {targha}\n'
	
	# Convert shadow output into dictionary
	d = string_to_dict(line,pattern)
	
	# Convert some dictionary keys from dms to deg or hms to hr
	d['ra'] = convert2dec(d,['ra_h','ra_m','ra_s'])
	d['dec'] = convert2dec(d,['dec_d','dec_m','dec_s'])
	d['last'] = convert2dec(d,['last_h','last_m','last_s'])
	d['glon'] = convert2dec(d,['glon_h','glon_m','glon_s'])
	d['glat'] = convert2dec(d,['glat_d','glat_m','glat_s'])
	
	# Convert strings to floats, except for the utc string
	utc = d.pop('utc') # Put 'utc' in safe-keeping
	shdw={}
	for x in d.items():
		shdw[x[0]]=float(x[1]) # Convert each item to a float
	shdw['utc'] = utc # Put 'utc' back in dictionary
	return shdw
	
####################################################################################################
## Convert Datetime objects into Shadow-friendly strings
#  Not dependent on LYAO driver

def dt2shd(dt):
	return dt.strftime("%Y %m %d %H %M %S")

####################################################################################################
# Create LYAO inputs_los.dat file from Shadow DataFrame
# ****DEPENDENT ON LYAO DRIVER****

def shd2los(shdwdf,fout):
	# Susan's WHAM driver (driver_WHAMSUSANZEN.dat) looks for four input columns:
	# SZA, ZNTH, AZI, HSHAD
	sza = shdwdf.sunzd.tolist()
	znth = shdwdf.targzd.tolist()
	azi = shdwdf.diffaz.tolist()
	hshad = shdwdf.shdalt.tolist()
	rows = zip(sza,znth,azi,hshad)
	
	# The driver also looks for a header with five values:
	# (# of rows), (line label), (resonance wavelength), (branching ratio), (solar line center flux)
	n_rows = shdwdf.shape[0]
	llbl = 2
	waveln = 1025.72
	fluorb = 0.882
	fluxc = 1e9
	
	# Write LOS file
	id = open(fout,'w')
	id.write('%i\t%i\t%.3e\t%.3e\t%.4e\n'%(n_rows,llbl,waveln,fluorb,fluxc))
	for row in rows:
		id.write('%.1f    %.1f    %.1f    %.3f\n'%row)
	id.close()
	return None

####################################################################################################
## Parse USNO Calendar and output USNO DataFrame
#  Not dependent on LYAO driver

def USNOparser(fpath):
	id = open(fpath)
	lines = id.readlines()
	id.close()

	months = [datetime(2000,x+1,21).strftime('%b') for x in range(0,12)]
	
	dates = [line[:2] for line in lines[9:-3]]

	dcln = [line[2:-1] for line in lines[9:-3]]
	d = [[line[i:i+11] for i in range(0,len(line),11)] for line in dcln]
	usnodf=pd.DataFrame()
	for i,row in enumerate(d):
		s=pd.Series([item.split() for item in row])
		usnodf = usnodf.append(s,ignore_index=True)
	usnodf.columns = months
	usnodf.index = dates
	usnodf.index.name = 'Day'
	return usnodf

####################################################################################################
## Use USNO DataFrame to create time-of-day constraints for a particular date
#  Not dependent on LYAO driver

def dt2tod(dt,usnodf,UTCoffset,option='default'):
	# handle PM	
	if option=='ctio':
		AMhr = 9 + UTCoffset #9AM
		PMhr = 15 + UTCoffset #3PM
		PMmn = 0	
	else:	
		day,mo = dt.strftime('%d'),dt.strftime('%b')
		PMtm = usnodf.loc[day,mo]
		PMhr = int(PMtm[1][0:2])
		PMmn = int(PMtm[1][2:4])
		AMtm = usnodf.loc[day,mo]
		AMhr = int(AMtm[0][0:2])
		AMmn = int(AMtm[0][2:4])

	# handle AM
	if PMhr > AMhr:
		AMdoy = int(dt.strftime('%-j')) + 1
		isnewyear = ((isleap(dt.year)and(AMdoy>366))or(not isleap(dt.year)and(AMdoy>365)))
		AMdoy = 1 if isnewyear else AMdoy
		y = dt.year+1 if isnewyear else dt.year
		AMdt = datetime.strptime('%i %i'%(y,AMdoy),'%Y %j')
	else:
		AMdt=dt
	if option=='ctio':
		AMhr = 9 + UTCoffset #9AM
		AMmn = 0
	else:
		day,mo = AMdt.strftime('%d'),AMdt.strftime('%b')
		AMtm = usnodf.loc[day,mo]
		AMhr = int(AMtm[0][0:2])
		AMmn = int(AMtm[0][2:4])

	# return
	AM = dt2shd(AMdt.replace(hour=AMhr,minute=AMmn))
	PM = dt2shd(dt.replace(hour=PMhr, minute=PMmn))
	midnight = dt2shd(AMdt.replace(hour=UTCoffset))
	return [AM,PM,midnight]


####################################################################################################
## Writes the RT inputs string
#  Not dependent on LYAO driver

#  Defaults to MSIS/Chamberlain Evaporative Case and Lyman Beta, i.e.
#  LINE_LABEL = 2
#  MSISFLAG = -1
#  DEXO, DPEAK, DBASE = [-1, -1, -1]
#  IGEOFLAG = 1
#  SATT, SATD = [1000 -1]

def RTinputstr(loc,time,f107,Ap,line_label=2,msisflag=-1,
		Hpar=[-1,-1,-1],igeoflag=1,sat=(1000, -1)):
	# Handle Location Input
	locdic={"pbo":(43.0776,-89.6717),
		"ctio":(-30.172509,-70.799266),
		"kpno":(31.9599,-111.5997)}	
	
	if loc in locdic:
		lat,lon = locdic[loc]
	else:
		lat,lon = loc
	# Handle Time Input
	doy = time.strftime('%-j')
	year = time.strftime('%y')
	tm = time.hour + time.minute/60 + time.second/(60*60)

	# Write RT
	RT=[]
	RT.append('%i\n'%line_label)
	RT.append('%.4f %.4f\n'%(lat,lon))
	RT.append('%s %s\n'%(doy,year))
	RT.append('%.2f\n'%tm)
	RT.append('0 %.1f 0.0 0.0 0.0 0.0 0.0 0.0\n'%Ap)
	RT.append('%.1f %.1f\n'%(f107,f107))
	RT.append('%i  %.1e  %.1e  %.1e\n'%(msisflag,Hpar[0],Hpar[1],Hpar[2]))
	RT.append('%i  %i  %.1e\n'%(igeoflag,sat[0],sat[1]))
	return RT

####################################################################################################
## Writes the RT inputs string to "infile.dat" within the LYAO_RT directory
#  Not dependent on LYAO driver

def writeRTinput(fpath,RT):
	id = open(fpath+"infile.dat",'w')
	for rt in RT:
		id.write(rt)
	id.close()
	return None



