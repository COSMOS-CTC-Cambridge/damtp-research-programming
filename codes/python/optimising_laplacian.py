
import numpy
import scipy
import scipy.fftpack 
import cProfile
import time as timemod
import pstats
import os

def Laplacian0(data, lapl, d, N):
    for kk in range(1,data.shape[2]-1):
        for jj in range(1,data.shape[1]-1):
            for ii in range(1,data.shape[0]-1):
                lapl[ii,jj,kk] = (
                    (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])/(d[0]*d[0]) +
                    (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])/(d[1]*d[1]) +
                    (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])/(d[2]*d[2]))
    return

def Laplacian1(data, lapl, d, N):
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

def Laplacian2(data, lapl, d, N):
    lapl[1:-1,1:-1,1:-1] = (
        (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])/(d[0]*d[0]) +
        (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])/(d[1]*d[1]) +
        (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])/(d[2]*d[2]))
    return

def RunOne(prof, func, *args):
    prof.runcall(func, *args)
    return

def GetLtime(prof, function):
    p=pstats.Stats(prof[function])
    Ltime=[p.stats[x] for x in p.stats if x[2].startswith(function) or x[2].startswith("<"+function) or x[2].endswith(function+">")][0][2]
    return Ltime

def RunSome(funcflops):
    variables = Init(SIZE)
    if ("OMP_NUM_THREADS" in os.environ):
        threads = int(os.environ["OMP_NUM_THREADS"])
    else:
        threads = 1
    cp={}
    times={}
    funcs = [func["func"] for func in funcflops]
    for funcflop in funcflops:
        function=funcflop["func"]
        LGF=funcflop["flop"]
        cp[function]=cProfile.Profile()
        start = timemod.clock()
        RunOne(cp[function], eval(function), variables["data"], variables["laplacian"], variables["lattice_spacing"], threads)
        end = timemod.clock()
        times[function] = GetLtime(cp,function)
        print("{func} executed in {time} (or {timemod}) at {GFps} GF/s".format(func=function,
                                                                               time=times[function],
                                                                               GFps=LGF/times[function]/1e9,
                                                                               timemod=end-start))
    print("Speedup between {f0} and {fN}: {slowfast}".format(slowfast=times[funcs[0]]/times[funcs[-1]],
                                                             f0=funcs[0], fN=funcs[-1]))
    if (len(times)>1):
        print("Speedup between {fNm1} and {fN}: {slowfast}".format(slowfast=times[funcs[-2]]/times[funcs[-1]],
                                                             fNm1=funcs[-2], fN=funcs[-1]))
    return (cp,times)

SIZE=100
RunList=[{"func":"Laplacian2", "flop":(SIZE-2)**3*17}]
results = RunSome([
    {"func":"Laplacian0", "flop":(SIZE-2)**3*17},
    {"func":"Laplacian1", "flop":(SIZE-2)**3*17}]+RunList)

def Laplacian3(data, lapl, d, N):
    dx2, dy2, dz2 = 1./(d[0]*d[0]), 1./(d[1]*d[1]), 1./(d[2]*d[2])
    lapl[1:-1,1:-1,1:-1] = (
        (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])*dx2 +
        (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])*dy2 +
        (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])*dz2)
    return

SIZE=200
RunList.append({"func":"Laplacian3", "flop":(SIZE-2)**3*14+3})
results = RunSome(RunList)

import pyximport
pyximport.install(setup_args={'include_dirs': numpy.get_include()})
import sys
sys.path = ["../codes/python"]+sys.path
import cyLaplacian1
RunList.append({"func":"cyLaplacian1.cyLaplacian1", "flop":(SIZE-2)**3*14+3})
results = RunSome(RunList)

import cyLaplacian2
RunList.append({"func":"cyLaplacian2.cyLaplacian2", "flop":(SIZE-2)**3*14+3})
results = RunSome(RunList)

import cyLaplacian3
RunList.append({"func":"cyLaplacian3.cyLaplacian3", "flop":(SIZE-2)**3*14+3})
results = RunSome(RunList)

import cyLaplacian4
RunList.append({"func":"cyLaplacian4.cyLaplacian3", "flop":(SIZE-2)**3*14+3})
results = RunSome(RunList)

import cyLaplacian5
RunList.append({"func":"cyLaplacian5.cyLaplacian5", "flop":(SIZE-2)**3*14+3})
results = RunSome(RunList)

import cyLaplacian6
SIZE=500
RunList.append({"func":"cyLaplacian6.cyLaplacian6", "flop":(SIZE-2)**3*14+3})
RunList = [{"func":x["func"], "flop":(SIZE-2)**3*14+3} for x in RunList[1:]]
results = RunSome(RunList)

AnotherRunList=[{"func":"cyLaplacian7", "flop":(SIZE-2)**3*(14+6*5+6+3)+3}]
RunSome(RunList[-1:]+AnotherRunList)
