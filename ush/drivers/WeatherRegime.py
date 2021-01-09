import os
import numpy as np
from netCDF4 import Dataset
from pylab import *
from sklearn.cluster import KMeans
from scipy import stats,signal
from numpy import ones,vstack
from numpy.linalg import lstsq
from metplus.util import config_metplus, get_start_end_interval_times, get_lead_sequence
from metplus.util import get_skip_times, skip_time, is_loop_by_init, ti_calculate
from Blocking_WeatherRegime_util import read_nc_met

class WeatherRegimeCalculation():
    """Contains the programs to perform a Weather Regime Analysis
    """
    def __init__(self,config,label):

        self.invar = config.getstr('WeatherRegime',label+'_WR_VAR','')
        self.wrnum = config.getint('WeatherRegime',label+'_WR_NUMBER',6)
        self.numi = config.getint('WeatherRegime',label+'_NUM_CLUSTERS',20)


    def get_cluster_fraction(self, m, label):
        return (m.labels_==label).sum()/(m.labels_.size*1.0)


    def weights_detrend(self,lats,lons,indata):

        ##Set up weight array
        cos = lats * np.pi / 180.0
        way = np.cos(cos)
        weightf = np.repeat(way[:,np.newaxis],len(lons),axis=1)

        #Remove trend and seasonal cycle
        atemp = np.zeros(indata.shape)
        for i in np.arange(0,len(indata[0,:,0,0]),1):
            atemp[:,i] = signal.detrend(atemp[:,i],axis=0)
            atemp[:,i] = (indata[:,i] - np.nanmean(indata[:,i],axis=0)) * weightf

        a = atemp
        atemp=0

        #Reshape into time X space
        a1 = np.reshape(a,[len(a[:,0,0,0])*len(a[0,:,0,0]),len(lons)*len(lats)])

        return a,a1


    def run_elbow(self,elbowinfiles,elbowyrs):
        wrnum=6
        k=KMeans(n_clusters=wrnum, random_state=0, n_jobs=-1)  #Initilize cluster centers

        a,lat,lon,yr = read_nc_met(elbowinfiles,elbowyrs,self.invar)

        #var = 'Z500'
        #file1 = '/glade/work/demiller/ERAi/Z/Z500day/Z500dayDJF.nc'
        #f1 = Dataset(file1, mode="r")
        #dec = f1.variables[var][:]
        #a=np.array(dec)
        #f1.close()

        #Set your domain. Limits below specify US
        lon1=230
        lon2=301
        lat1=35 #index, lat = 90-lat1
        lat2=66 #index, lat = 90-lat2

        a = a[:,:,lat1:lat2,lon1:lon2]

        #US Lats and lons
        lat = np.arange(90-lat1,90-lat2,-1)
        lon = np.arange(lon1,lon2,1)

        a,a1 = self.weights_detrend(lat,lon,a)
        ##Set up weight array
        #cos = lat * np.pi / 180.0
        #way = np.cos(cos)
        #weightf = np.repeat(way[:,np.newaxis],len(lon),axis=1)

        #Remove trend and seasonal cycle
        #atemp = np.zeros(a.shape)
        #for i in np.arange(0,len(a[0,:,0,0]),1):
        #    atemp[:,i] = signal.detrend(atemp[:,i],axis=0)
        #    atemp[:,i] = (a[:,i] - np.nanmean(a[:,i],axis=0)) * weightf

        #a = atemp
        #atemp=0

        #Reshape into time X space
        #a1 = np.reshape(a,[len(a[:,0,0,0])*len(a[0,:,0,0]),len(lon)*len(lat)])

        #Calculate sum of squared distances for clusters 1-15
        kind = np.arange(1,self.numi,1)
        Sum_of_squared_distances = []
        K = range(1,self.numi)
        for k in K:
            km = KMeans(n_clusters=k)
            km = km.fit(a1)
            Sum_of_squared_distances.append(km.inertia_)

        # Calculate the bend of elbow
        points = [(K[0],Sum_of_squared_distances[0]),(K[-1],Sum_of_squared_distances[-1])]
        x_coords, y_coords = zip(*points)
        A = vstack([x_coords,ones(len(x_coords))]).T
        m, c = lstsq(A, y_coords,rcond=None)[0]
        line = m*kind + c
        curve = Sum_of_squared_distances
        curve=np.array(curve)*10**-10
        line = line*10**-10

        d=[]
        for i in np.arange(0,self.numi-1,1):
            p1=np.array([K[0],curve[0]])
            p2=np.array([K[-1],curve[-1]])
            p3=np.array([K[i],curve[i]])
            d=np.append(d,np.cross(p2-p1,p3-p1)/np.linalg.norm(p2-p1))

        mi = np.where(d==d.min())[0]
        print('Optimal Cluster # = '+str(mi+1)+'')

        print(line)
        print(curve)
        exit()
        return a,lat,lon,yr,K,d,mi,line,curve


    def Calc_EOF(self,Z500in,lats,lons):

        #Set your domain. Limits below specify US
        lon1=230
        lon2=301
        lat1=35 #index, lat = 90-lat1
        lat2=66 #index, lat = 90-lat2

        a = a[:,:,lat1:lat2,lon1:lon2]

        #US Lats and lons
        lat = np.arange(90-lat1,90-lat2,-1)
        lon = np.arange(lon1,lon2,1)

        eofin = a #signal.detrend
        #Remove trend and seasonal cycle
        for d in np.arange(0,len(eofin[0,:,0,0]),1):
            eofin[:,d] = signal.detrend(eofin[:,d],axis=0)
            eofin[:,d] = eofin[:,d] - np.nanmean(eofin[:,d],axis=0)

        #Reshape into time X space
        eofin = np.reshape(eofin,(len(eofin[:,0,0,0])*len(eofin[0,:,0,0]),len(eofin[0,0,:,0])*len(eofin[0,0,0,:])))

        # Use EOF solver and get PCs and EOFs
        solver = Eof(eofin,center=False)
        pc = solver.pcs(npcs=NUMPCS,pcscaling=1)
        eof = solver.eofsAsCovariance(neofs=NUMPCS,pcscaling=1)
        eof = np.reshape(eof,(NUMPCS,len(lats),len(lons)))

        #Get variance fractions
        variance_fractions = solver.varianceFraction(neigs=10) * 100
        print(variance_fractions)

        lonext=lons
        latext=lats

        return


    def run_K_means(self,Z500in,lats,lons):

        #Set your domain. Limits below specify US
        lon1=230
        lon2=301
        lat1=35 #index, lat = 90-lat1
        lat2=66 #index, lat = 90-lat2

        a = a[:,:,lat1:lat2,lon1:lon2]

        #US Lats and lons
        lat = np.arange(90-lat1,90-lat2,-1)
        lon = np.arange(lon1,lon2,1)

        a,a1 = self.weights_detrend(lats,lons,z500in)

        #fit the K-means algorithm to the data
        f=k.fit(a1)

        #Obtain the cluster anomalies
        y=f.cluster_centers_

        #Obtain cluster labels for each day [Reshape to Year,day]
        wr = f.labels_
        wr = np.reshape(wr,[len(a[:,0,0,0]),len(a[0,:,0,0])])

        yf = np.reshape(y,[self.wrnum,len(lat),len(lon)]) # reshape cluster anomalies to latlon

        #Get frequency of occurence for each cluster
        perc=np.zeros(self.wrnum)
        for ii in np.arange(0,self.wrnum,1):
            perc[ii] = get_cluster_fraction(f,ii)

        #Sort % from low to high
        ii = np.argsort(perc)
        print(perc[ii])

        #Reorder
        perc = perc[ii]
        input=yf[ii]
        ii = ii[::-1]

        #Reorder from max to min and relabel
        wrc = wr*1.0/1.0
        for i in np.arange(0,self.wrnum,1):
            wrc[wr==ii[i]] = i

        perc = perc[::-1]
        input = input[::-1]

        #Save Label data [YR,DAY]
        np.save('WR_LABELS',wrc)
        print(wr.shape)

        return
