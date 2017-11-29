import numpy
import scipy
import scipy.fftpack 
import cProfile
import time as timemod
import os

def Laplacian(data, lapl, d):
    for ii in range(1,data.shape[0]-1):
        for jj in range(1,data.shape[1]-1):
            for kk in range(1,data.shape[2]-1):
                lapl[ii,jj,kk] = (
                    (data[ii-1,jj,kk] -
                     2*data[ii,jj,kk] + data[ii+1,jj,kk])/(d[0]*d[0]) +
                    (data[ii,jj-1,kk] -
                     2*data[ii,jj,kk] + data[ii,jj+1,kk])/(d[1]*d[1]) +
                    (data[ii,jj,kk-1] -
                     2*data[ii,jj,kk] + data[ii,jj,kk+1])/(d[2]*d[2]))
    return

def Init(size):
    d=numpy.array([0.1,0.1,0.1])
    data=numpy.random.random([size]*3)
    lapl=numpy.zeros_like(data)
    return {"data": data, "laplacian": lapl, "lattice_spacing": d}

def Fourier(data):
    return scipy.fftpack.fftn(data)

def AddLittle(data):
    for ii in range(0,data.shape[0]):
        for jj in range(0,data.shape[1]):
            for kk in range(0,data.shape[2]):
                data[ii,jj,kk] = data[ii,jj,kk] + 1./numpy.pi
    return

def IFourier(data):
    return scipy.fftpack.ifftn(data)

def WriteToFile(data):
    filename="ihopethisfiledoesnotexist.dat"
    data.tofile(filename, sep=" ")
    return filename

def DestroyFile(filename):
    os.unlink(filename)
    return

def RunProfile(size):
    variables = Init(size)
    Laplacian(variables["data"], variables["laplacian"],
              variables["lattice_spacing"])
    fftdata=Fourier(variables["data"])
    AddLittle(fftdata) # pass-by-reference, so OUR fftdata WILL CHANGE
    finaldata=IFourier(fftdata)
    filename=WriteToFile(finaldata)
    return filename

SIZE=100
cp=cProfile.Profile()
start = timemod.clock()
fn=cp.runcall(RunProfile, SIZE)
end = timemod.clock()
DestroyFile(fn)
print("cProfile gave total time of {time} s ".format(time=end-start)+
      "and the following profile.")
cp.print_stats(sort="time")

import pstats
p=pstats.Stats(cp)
Ltime=[p.stats[x] for x in p.stats if x[2]=="Laplacian"][0][2]
LGF=(SIZE-2)**3*17
print("Laplacian executed in {time} at {GFps} GF/s".format(
    time=Ltime, GFps=LGF/Ltime/1e9))
