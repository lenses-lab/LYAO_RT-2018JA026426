import os
import matplotlib.pyplot as plt
from scipy.interpolate import griddata
import numpy as np
from lyao_parse import *

loc='pbo'
path = os.path.abspath(os.path.dirname(sys.argv[0]))+"/"
dp = path+"../%s_finegrid/"%loc.upper()

doys = list(range(1,367))

solruns,mxs,mns = [],[],[]
for f107 in [70,210]:
	doyruns=[]
	for doy in doys:
		runs = []
		for tm in ["AM","PM"]:
			fp = dp+"DOY_%i/f107_%i/%s"%(doy,f107,tm)
			#print(fp)
			run = LYAO_RT(fp)
			runs.append(run)
			mxs.append(np.max(run.los.shdalt))
			mns.append(np.min(run.los.shdalt))
		doyruns.append(runs)
	solruns.append(doyruns)
	
AM,PM=0,1
shdalt,igeo=0,1

mx_shdalt = np.min(mxs)
mn_shdalt = np.max(mns)

xi = np.linspace(1,366,366)
yi = np.linspace(mn_shdalt,mx_shdalt,100)

# Set up Plotting Axes
fig = plt.gcf()
fig.set_size_inches(8.67, 5.38)
fig.suptitle(r'LYAO_RT/MSIS-00 at %s'%loc.upper())
gridsz = [len(solruns),3]
grid = plt.GridSpec(gridsz[0],gridsz[1],wspace=0.6,hspace=0.6)
axes=[]
for x in range(0,gridsz[0]):
	for y in range(0,gridsz[1]):
		axes.append(fig.add_subplot(grid[x,y]))
ts = ['Min','Max']
SLCflux = [5,9]
		
# Create data array
for i,solrun in enumerate(solruns):
	AMdoys,PMdoys=[],[]
	AMsas,PMsas=[],[]
	AMints,PMints=[],[]
	for doy,doyrun in zip(doys,solrun):
		
		AMint = list(zip([doy]*len(doyrun[AM].los.shdalt),doyrun[AM].los.shdalt,doyrun[AM].los.Ha_int))
		PMint = list(zip([doy]*len(doyrun[AM].los.shdalt),doyrun[PM].los.shdalt,doyrun[PM].los.Ha_int))
		AMfltr = list(filter(lambda x: x[0] < mx_shdalt, AMint))
		PMfltr = list(filter(lambda x: x[0] < mx_shdalt, PMint))
		AMlst = list(zip(*AMfltr))
		PMlst = list(zip(*PMfltr))
		AMint = [x*SLCflux[i] for x in list(AMlst[2])]
		PMint = [x*SLCflux[i] for x in list(PMlst[2])]
		
		AMdoys,PMdoys = AMdoys+list(AMlst[0]), PMdoys+list(PMlst[0])
		AMsas, PMsas = AMsas+list(AMlst[1]), PMsas+list(PMlst[1])
		AMints, PMints = AMints+AMint, PMints+PMint
	
	mx_Ha_int = np.max(AMints+PMints)
	
	AMzi = griddata((AMdoys,AMsas),AMints,(xi[None,:], yi[:,None]),method='cubic')
	PMzi = griddata((PMdoys,PMsas),PMints,(xi[None,:], yi[:,None]),method='cubic')
	
	c=axes[3*i].pcolor(xi,yi,AMzi,vmin=0,vmax=9,cmap="plasma")
	axes[3*i].set_title('Solar %s, AM'%ts[i])
	axes[3*i].set_ylabel('Shadow Altitude')
	axes[3*i].set_xlabel('Day Number of Year')
	#axes[3*i].set_ylim(350,650)
	cb=fig.colorbar(c,ax=axes[3*i],ticks=[2,4,6,8])
	cb.set_label(r'H-$\alpha$ Intensity (R)')
	
	c=axes[3*i+1].pcolor(xi,yi,PMzi,vmin=0,vmax=9,cmap="plasma")
	axes[3*i+1].set_title('Solar %s, PM'%ts[i])
	axes[3*i+1].set_ylabel('Shadow Altitude')
	axes[3*i+1].set_xlabel('Day Number of Year')
	#axes[3*i+1].set_ylim(350,650)
	cb=fig.colorbar(c,ax=axes[3*i+1],ticks=[2,4,6,8])
	cb.set_label(r'H-$\alpha$ Intensity (R)')
	
	ratio = [a/p for a,p in zip(AMzi,PMzi)]
	
	c=axes[3*i+2].pcolor(xi,yi,ratio,vmin=0.7,vmax=1.3,cmap="coolwarm")
	axes[3*i+2].set_title('Solar %s, AM/PM'%ts[i])
	axes[3*i+2].set_ylabel('Shadow Altitude')
	axes[3*i+2].set_xlabel('Day Number of Year')
	#axes[3*i+2].set_ylim(350,650)
	cb=fig.colorbar(c,ax=axes[3*i+2],ticks=[.6,.8,1.0,1.2,1.4])
	cb.set_label(r'H-$\alpha$ Intensity Ratio AM/PM')
	
fig.savefig(path+"%s_int-doy.png"%loc.upper())
plt.show()