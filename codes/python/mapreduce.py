#!/usr/bin/env python

import mpi4py
from mpi4py import MPI
import numpy

'''
Map/Reduce in python

A very simple example where a "big" array is reduced (sum): each rank reduces their own
bit and then we Reduce() to "master".
'''

def get_data():
    len = 1e7
    loclen = numpy.ceil(len*1.0/MPI.COMM_WORLD.Get_size())
    myrank=MPI.COMM_WORLD.Get_rank()
    return numpy.arange(loclen*myrank, min(len,loclen*(1+myrank)))
    
def lmap(data):
    sum = numpy.array([data.sum()])
    return sum

def greduce(localval):
    redsum = numpy.zeros_like(localval)*numpy.nan
    MPI.COMM_WORLD.Reduce([localval, MPI.DOUBLE], [redsum, MPI.DOUBLE], op=MPI.SUM,
                          root=0)
    return redsum

if ("__main__" == __name__):
    result = greduce(lmap(get_data()))
    if (MPI.COMM_WORLD.Get_rank() == 0):
        print result
