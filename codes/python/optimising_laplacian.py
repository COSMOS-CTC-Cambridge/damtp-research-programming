
import numpy
import scipy
import scipy.fftpack 
import cProfile
import time as timemod
import pstats

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

def Laplacian2(data, lapl, d):
    lapl = (
        (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])/(d[0]*d[0]) +
        (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])/(d[1]*d[1]) +
        (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])/(d[2]*d[2]))
    return

def RunOne(prof, func, *args):
    prof.runcall(func, *args)
    return

def GetLtime(prof, function):
    p=pstats.Stats(prof[function])
    Ltime=[p.stats[x] for x in p.stats if x[2].startswith(function) or x[2].startswith("<"+function)][0][2]
    return Ltime

def RunSome(funcflops):
    variables = Init(SIZE)
    cp={}
    times={}
    funcs = [func["func"] for func in funcflops]
    for funcflop in funcflops:
        function=funcflop["func"]
        LGF=funcflop["flop"]
        cp[function]=cProfile.Profile()
        RunOne(cp[function], eval(function), variables["data"], variables["laplacian"], variables["lattice_spacing"])
        times[function] = GetLtime(cp,function)
        print("{func} executed in {time} at {GFps} GF/s".format(func=function, time=times[function], GFps=LGF/times[function]/1e9))
    print("Speedup between {f0} and {fN}: {slowfast}".format(slowfast=times[funcs[0]]/times[funcs[-1]],
                                                             f0=funcs[0], fN=funcs[-1]))
    if (len(times)>1):
        print("Speedup between {fNm1} and {fN}: {slowfast}".format(slowfast=times[funcs[-2]]/times[funcs[-1]],
                                                             fNm1=funcs[-2], fN=funcs[-1]))
    return (cp,times)

SIZE=100
results = RunSome([{"func":"Laplacian", "flop":(SIZE-2)**3*17},
                   {"func":"Laplacian2", "flop":(SIZE-2)**3*17}])

def Laplacian3(data, lapl, d):
    dx2, dy2, dz2 = d[0]*d[0], d[1]*d[1], d[2]*d[2]
    lapl = (
        (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])/dx2 +
        (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])/dy2 +
        (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])/dz2)
    return

SIZE=400
results = RunSome([{"func":"Laplacian2", "flop":(SIZE-2)**3*17},
                   {"func":"Laplacian3", "flop":(SIZE-2)**3*14+3}])

import pyximport
pyximport.install()
import sys
sys.path = ["./codes/python"]+sys.path
import cyLaplacian
results = RunSome([{"func":"Laplacian2", "flop":(SIZE-2)**3*17},
                   {"func":"Laplacian3", "flop":(SIZE-2)**3*14+3},
                   {"func":"cyLaplacian.cyLaplacian1", "flop":(SIZE-2)**3*14+3}])
