
import numpy
import scipy
import scipy.fftpack 
import cProfile
import time as timemod

def Init(sizes):
    return 

def Laplacian(data, lapl, d):
    for ii in range(1,data.shape[0]-1):
        for jj in range(1,data.shape[1]-1):
            for kk in range(1,data.shape[2]-1):
                lapl[ii,jj,kk] = (
                    (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])/(d[0]*d[0]) +
                    (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])/(d[1]*d[1]) +
                    (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])/(d[2]*d[2]))
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
    data.tofile("ihopethisfiledoesnotexist.dat", sep=" ")
    return

def RunProfile(size):
    variables = Init(size)
    Laplacian(variables["data"], variables["laplacian"], variables["lattice_spacing"])
    fftdata=Fourier(variables["data"])
    AddLittle(fftdata) # pass-by-reference, so OUR fftdata WILL CHANGE
    finaldata=IFourier(fftdata)
    WriteToFile(finaldata)
    
SIZE=100
cp=cProfile.Profile()
start = timemod.clock()
cp.runcall(RunProfile, SIZE)
end = timemod.clock()
print("cProfile gave total time of {time} s and the following profile.".format(time=end-start))
cp.print_stats(sort="time")

import pstats
p=pstats.Stats(cp)
Ltime=[p.stats[x] for x in p.stats if x[2]=="Laplacian"][0][2]
LGF=(SIZE-2)**3*15
print("Laplacian executed in {time} at {GFps} GF/s".format(time=Ltime, GFps=LGF/Ltime/1e9))

def Laplacian2(data, lapl, d):
    lapl = (
        (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])/(d[0]*d[0]) +
        (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])/(d[1]*d[1]) +
        (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])/(d[2]*d[2]))
    return

LGF=(SIZE-2)**3*15
  
def RunOne(prof, func, *args):
    prof.runcall(func, *args)

def GetLtime(prof):
    p=pstats.Stats(prof)
    Ltime=[p.stats[x] for x in p.stats if x[2].startswith("Laplacian")][0][2]
    return Ltime

def RunSome(funcs):
    variables = Init(SIZE)
    cp={}
    times={}
    for function in funcs:
        cp[function]=cProfile.Profile()
        RunOne(cp[function], eval(function), variables["data"], variables["laplacian"], variables["lattice_spacing"])
        times[function] = GetLtime(cp[function])
        print("{func} executed in {time} at {GFps} GF/s".format(func=function, time=Ltime, GFps=LGF/Ltime/1e9))
    print("Speedup between {f0} and {fN}: {slowfast}".format(slowfast=times[funcs[0]]/times[funcs[-1]],
                                                             f0=funcs[0], fN=funcs[-1]))
    if (len(times)>1):
        print("Speedup between {fNm1} and {fN}: {slowfast}".format(slowfast=times[funcs[-2]]/times[funcs[-1]],
                                                             fNm1=funcs[-2], fN=funcs[-1]))
    return (cp,times)

results = RunSome(["Laplacian", "Laplacian2"])
