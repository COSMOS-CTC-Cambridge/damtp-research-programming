#!/usr/bin/env python3
import time
import numpy
import mpi4py
from mpi4py import MPI

def ping_master(masterrank):
    times = []
    for rank in range(MPI.COMM_WORLD.size):
        if rank != masterrank:
            t1 = time.clock()
            data = numpy.array([1.0])
            MPI.COMM_WORLD.Send([data, MPI.DOUBLE], dest=rank, tag=0)
            MPI.COMM_WORLD.Recv([data, MPI.DOUBLE], source=rank, tag=0)
            t2 = time.clock()
            times.append(t2-t1)
    print("Average ping-pong time was {av}.".format(av=sum(times)/len(times)))
    return

def ping_slave(masterrank):
    data = numpy.array([1])
    MPI.COMM_WORLD.Recv([data, MPI.DOUBLE], source=masterrank, tag=0)
    MPI.COMM_WORLD.Send([data, MPI.DOUBLE], dest=masterrank, tag=0)
    return

def pingpong():
    masterrank = 0
    if MPI.COMM_WORLD.rank == masterrank:
        ping_master(masterrank)
    else:
        ping_slave(masterrank)
    return

def pass_along(startrank):
    up = (MPI.COMM_WORLD.rank + 1) % MPI.COMM_WORLD.size
    down = (MPI.COMM_WORLD.rank - 1) % MPI.COMM_WORLD.size
    data = numpy.array([1.])
    ten_primes = numpy.array([2, 3, 5, 7, 11, 13, 17, 19, 23, 29])
    if (MPI.COMM_WORLD.rank == startrank):
        data = data * ten_primes[MPI.COMM_WORLD.rank]
        MPI.COMM_WORLD.Send([data, MPI.DOUBLE], dest=up, tag=0)
        MPI.COMM_WORLD.Recv([data, MPI.DOUBLE], source=down, tag=0)
        success = numpy.array([numpy.allclose(ten_primes[:MPI.COMM_WORLD.size].prod(), data)]).astype("int")
        if (MPI.COMM_WORLD.rank != 0):
            MPI.COMM_WORLD.Send([success, MPI.INT], dest=0, tag=1)
    else:
        MPI.COMM_WORLD.Recv([data, MPI.DOUBLE], source=down, tag=0)
        data = data * ten_primes[MPI.COMM_WORLD.rank]
        MPI.COMM_WORLD.Send([data, MPI.DOUBLE], dest=up, tag=0)
    if (MPI.COMM_WORLD.rank == 0):
        if (startrank != 0):
            sucval = numpy.array([False]).astype("int")
            MPI.COMM_WORLD.Recv([sucval, MPI.INT], source=startrank, tag=1)
        else:
            sucval = success
        print("Success was {s}.".format(s=sucval.astype("bool")[0]))
    return

def ring():
    '''Send "up" receive from "down" but don't start from 0, but a random rank'''
    if (MPI.COMM_WORLD.rank == 0):
        startrank = numpy.random.randint(0,MPI.COMM_WORLD.size,1)
    else:
        startrank = numpy.array([0])
    MPI.COMM_WORLD.Bcast([startrank, MPI.INT], root=0)
    print("Starting ring from {}".format(startrank))
    pass_along(startrank)
    return

pingpong()
ring()
