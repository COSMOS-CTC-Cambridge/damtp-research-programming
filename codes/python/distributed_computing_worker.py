#!/usr/bin/env python

import numpy
import mpi4py
from mpi4py import MPI

class rankinfo(object):
    '''
    Holds some information about an MPI rank; ndim and periods are literals as they need
    to be the same across all ranks in our example.
    '''
    ndim=3
    periods=[False, True, True]
    stencil_width = 1
    def __init__(self, sizes):
        self.rank=MPI.COMM_WORLD.Get_rank()
        self.size=MPI.COMM_WORLD.Get_size()
        self.localsizes=[x+rankinfo.stencil_width*2 for x in sizes]

class topology(object):
    def __init__(self, rankinfo):
        self.me=rankinfo
        self.dims=MPI.Compute_dims(self.me.size, self.me.ndim)
        self.topology=MPI.COMM_WORLD.Create_cart(self.dims, periods=self.me.periods, reorder=True)
        self.left,self.right = self.topology.Shift(0,1)
        self.front,self.back = self.topology.Shift(1,1)
        self.up,self.down = self.topology.Shift(2,1)
    def print_info(self):
        coords = self.topology.Get_coords(self.me.rank)
        msg="I am rank {rank} and I live at {coords}.".format(
            rank=self.me.rank, coords=coords)
        msg = msg + "Inverse lookup of {coords} gives rank {rank}.".format(
            coords=coords,rank=self.topology.Get_cart_rank(coords))
        serialised_print(msg, self.topology)
        return

class ghost_data(object):
    def __init__(self, topology, sizes):
        self.types = sizes
        self.axes = topology
    @property
    def types(self):
        return self._types
    @types.setter
    def types(self, sizes):
        mx,my,mz = sizes
        Zds,Zdr,Zus,Zur=MPI.DOUBLE.Create_subarray(sizes, [mx,my,1], [0,0,1]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,my,1], [0,0,mz-1]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,my,1], [0,0,mz-2]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,my,1], [0,0,0]).Commit()
        Yds,Ydr,Yus,Yur=MPI.DOUBLE.Create_subarray(sizes, [mx,1,mz], [0,1,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,1,mz], [0,my-1,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,1,mz], [0,my-2,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,1,mz], [0,0,0]).Commit()
        Xds,Xdr,Xus,Xur=MPI.DOUBLE.Create_subarray(sizes, [1,my,mz], [1,0,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [1,my,mz], [mx-1,0,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [1,my,mz], [mx-2,0,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [1,my,mz], [0,0,0]).Commit()
        # Note: "down" and "up" refer to data movingg "downwards" and "upwards", so if one
        # rank sends data "down", that data is then moving "downwards" and must be
        # received by another rank with "down" argument as well
        self._types = {"X": {"send": {"down": Xds, "up": Xus}, "recv": {"down": Xdr, "up": Xur}},
                       "Y": {"send": {"down": Yds, "up": Yus}, "recv": {"down": Ydr, "up": Yur}},
                       "Z": {"send": {"down": Zds, "up": Zus}, "recv": {"down": Zdr, "up": Zur}}}
    @property
    def axes(self):
        return self._axes
    @axes.setter
    def axes(self, topology):
        self._axes = {"X": {"up":   {"dest": topology.up,    "source": topology.down},
                            "down": {"dest": topology.down,  "source": topology.up}},
                      "Y": {"up":   {"dest": topology.back,  "source": topology.front},
                            "down": {"dest": topology.front, "source": topology.back}},
                      "Z": {"up":   {"dest": topology.right, "source": topology.left},
                            "down": {"dest": topology.left,  "source": topology.right}}
        }
        return

def serialised_print(msg, topo):
    # serialised printing: be VERY careful with structures like this lest you get a deadlock:
    # every rank MUST eventually call the Barrier!
    myrank = topo.Get_rank()
    for rankid in range(0,topo.Get_size()):
        if (myrank == rankid):
            print(msg)
        topo.Barrier()

def ghost_exchange_start(topo, localarray, ghostdefs):
    commslist=[]
    for axis in ["X", "Y", "Z"]:
        for direction in ["up", "down"]:
            commslist.append(
                topo.topology.Irecv(
                    buf=[localarray, 1, ghostdefs.types[axis]["recv"][direction]],
                    source=ghostdefs.axes[axis][direction]["source"], tag=0))
    for axis in ["X", "Y", "Z"]:
        for direction in ["up", "down"]:
            commslist.append(
                topo.topology.Isend(
                    buf=[localarray, 1, ghostdefs.types[axis]["send"][direction]],
                    dest=ghostdefs.axes[axis][direction]["dest"], tag=0))
    return commslist

def ghost_exchange_finish(commslist):
    MPI.Request.Waitall(commslist)
    return

def testme(maxgrad, topology):
    '''In fact, the per-rank maximum occurs in z-direction at *non-ghosted* lattice point
    (xmax-1, ymax-1,0) for ranks at the "left" side of non-periodic "0" (=Z!) dimension
    where xmax, ymax, zmax refer to the maximum values in the *non-ghosted* lattice
    (i.e. sizes-parameter given to the constructor of rankinfo), and counting starts from
    the [1,1,1] of the ghosted lattice (i.e. first interior point); for all other ranks,
    the maximum is in y-direction at (0,ymax-1,zmax-1). I.e. is sizes==[3,4,5] these are
    at [3,4,1] and [1,4,5] of the ghosted lattice

    The value at *non-ghosted* [x,y,z] == (z+zmax*(y+ymax*(x))+rank)**2, so for the whole
    ghosted lattice the value at [x+1,y+1,z+1] == (z+zmax*(y+ymax*(x))+rank)**2.

    Hence the expected per-rank maximum is for ranks at "left" boundary (recall the
    boundary condition is lattice[boundary]=0):

    max1 = (((0+1)+zmax*((ymax-1)+ymax*(xmax-1))+rank)**2-0)/2

    and the other ranks have (note that the y-direction is periodic, so ymax means 1):

    max2 = (((zmax-1)+zmax*((1)+ymax*(0))+rank)**2-((zmax-1)+zmax*((ymax-2)+ymax*(0))+rank)**2)/2

    '''
    size=topology.topology.Get_size()
    rank=topology.topology.Get_rank()
    expected=[1568,1600,1640,1680,1720,1760,1800,1840]
    return maxgrad == expected[size-1]
    
def initialise_values(me):
    '''Local arrays need to be STENCIL*2 bigger than the "real world" in each dimension'''
    local_array = numpy.zeros(numpy.array(me.localsizes).prod()).reshape(me.localsizes)
    sw = me.stencil_width
    local_array[sw:-sw,sw:-sw,sw:-sw]=((numpy.arange((numpy.array(me.localsizes)-2*sw).prod())+me.rank)**2).reshape(numpy.array(me.localsizes)-2*sw)
    return local_array

def find_max_grad(topology, local_array, ghostdefs):
    commslist=ghost_exchange_start(topology, local_array, ghostdefs)
    # could do work here but NOT use ghost points!
    ghost_exchange_finish(commslist)
    gradients=numpy.array(numpy.gradient(local_array))[:,1:-1,1:-1,1:-1]
    maxgrad_local = numpy.array(gradients).max()
    maxgrad_global = numpy.zeros_like(maxgrad_local)
    topology.topology.Allreduce([maxgrad_local, MPI.DOUBLE],
                                [maxgrad_global, MPI.DOUBLE],
                                op=MPI.MAX)
    return maxgrad_local, maxgrad_global
