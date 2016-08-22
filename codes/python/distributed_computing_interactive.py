
#!/usr/bin/env python

import ipyparallel
c = ipyparallel.Client(profile="mpi", cluster_id="training_cluster_0")
directview=c[:]
directview.block=True
with directview.sync_imports():
    import numpy
    import mpi4py
    from mpi4py import MPI

class rankinfo(object):
    ndim=3
    periods=[False, True, True]
    stencil_width = 1
    def __init__(self, sizes):
        self.rank=MPI.COMM_WORLD.Get_rank()
        self.size=MPI.COMM_WORLD.Get_size()
        self.localsizes=[x+rankinfo.stencil_width*2 for x in sizes]
directview["rankinfo"]=rankinfo

def serialised_print(msg, topo):
    # serialised printing: be VERY careful with structures like this lest you get a deadlock:
    # every rank MUST eventually call the Barrier!
    myrank = topo.Get_rank()
    for rankid in range(0,topo.Get_size()):
        if (myrank == rankid):
            print(msg)
        topo.Barrier()
    return
directview["serialised_print"]=serialised_print

class topology(object):
    def __init__(self, rankinfo):
        self.me=rankinfo
        self.dims=MPI.Compute_dims(self.me.size, self.me.ndim)
        self.topology=MPI.COMM_WORLD.Create_cart(self.dims, periods=self.me.periods, reorder=True)
        left,right = self.topology.Shift(0,1)
        front,back = self.topology.Shift(1,1)
        up,down = self.topology.Shift(2,1)
        self.shifts={"X": {"up": up, "down": down},
                     "Y": {"up": back, "down": front},
                     "Z": {"up": right, "down": left}}
    def print_info(self):
        coords = self.topology.Get_coords(self.me.rank)
        msg="I am rank {rank} and I live at {coords}.".format(
            rank=self.me.rank, coords=coords)
        msg = msg + "Inverse lookup of {coords} gives rank {rank}.".format(
            coords=coords,rank=self.topology.Get_cart_rank(coords))
        serialised_print(msg, self.topology)
directview["topology"]=topology

class ghost_data(object):
    def __init__(self, topology, sizes):
        self.mx,self.my,self.mz = sizes
        self.types = {}
        self.axes = {}
        for axis in ["X", "Y", "Z"]:
            self.types[axis]={}
            self.axes[axis]={}
            for op in ["send", "recv"]:
                self.types[axis][op]={}
                for movements in [("up","down"), ("down","up")]:
                    movement, negmovement = movements
                    self.types[axis][op][movement] = MPI.DOUBLE.Create_subarray(sizes,
                                                                                self.get_plaq(axis),
                                                                                self.get_corner(axis,op,movement))
                    self.types[axis][op][movement].Commit()
                    self.axes[axis][movement]={"dest": topology.shifts[axis][movement],
                                               "source": topology.shifts[axis][negmovement]}
    def axis2basisvec(self, axis):
        return numpy.array([axis == "X", axis == "Y", axis == "Z"], dtype=numpy.float64)
    def get_plaq(self, axis):
        vec = self.axis2basisvec(axis)
        pl = [self.mx, self.my, self.mz]*(1-vec)+vec
        return list(pl)
    def get_corner(self, axis, sendrecv, movement):
        vec = self.axis2basisvec(axis)
        axis_size = [x[0] for x in ((self.mx, "X"), (self.my, "Y"), (self.mz, "Z")) if x[1]==axis][0]
        loc = vec*( (movement=="down") +
                    ((sendrecv=="send")*(movement=="up") or (sendrecv=="recv")*(movement=="down"))*(axis_size-2)
                )
        return list(loc)
directview["ghost_data"]=ghost_data

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
directview["ghost_exchange_start"]=ghost_exchange_start

def ghost_exchange_finish(commslist):
    MPI.Request.Waitall(commslist)
    return
directview["ghost_exchange_finish"]=ghost_exchange_finish

def initialise_values(me, topo):
    size = topo.topology.Get_size()
    local_array = numpy.zeros(me.localsizes)
    procsalong, periods, mycoord = topo.topology.Get_topo()
    mycorner = mycoord*numpy.array(me.localsizes)
    for z in xrange(me.localsizes[0]):
        for y in xrange(me.localsizes[1]):
            start = mycorner[2] + 5*(y+mycorner[1])*procsalong[2] + 3*5*(z+mycorner[0])*procsalong[1]*procsalong[2]
            stop = start + me.localsizes[2]
            local_array[z,y,:] = numpy.arange(start, stop, step=1)**2
    return local_array
directview["initialise_values"]=initialise_values

def compute_grad(topology, local_array, ghostdefs):
    commslist=ghost_exchange_start(topology, local_array, ghostdefs)
    # could do work here but NOT use ghost points!
    ghost_exchange_finish(commslist)
    gradients=numpy.array(numpy.gradient(local_array))[:,1:-1,1:-1,1:-1]
    return gradients
directview["compute_grad"]=compute_grad

def find_global_max(topology, local_array, ghostdefs):
    maxgrad_local = numpy.array(local_array).max()
    maxgrad_global = numpy.zeros_like(maxgrad_local)
    topology.topology.Allreduce([maxgrad_local, MPI.DOUBLE],
                                [maxgrad_global, MPI.DOUBLE],
                                op=MPI.MAX)
    return maxgrad_local, maxgrad_global
directview["find_global_max"]=find_global_max

def testme(maxgrad, topology):
    size=topology.topology.Get_size()
    rank=topology.topology.Get_rank()
    expected=[1650.0,7632.0,13032.0,32119.5]
    return maxgrad == expected[size-1]
directview["testme"]=testme

@directview.remote(block=False)
def main():
    me=rankinfo(sizes=[3,4,5])
    cartesian_topology=topology(me)
    ghosts = ghost_data(cartesian_topology, me.localsizes)
    cartesian_topology.print_info()
    local_array = initialise_values(me, cartesian_topology)
    gradients = compute_grad(cartesian_topology, local_array, ghosts)
    result_l, result_g = find_global_max(cartesian_topology, gradients, ghosts)
    serialised_print("Rank {rank} had max gradient {maxgrad_l} while the global was {maxgrad_g}."
                     .format(
                         rank=me.rank,
                         maxgrad_l=result_l,
                         maxgrad_g=result_g),
                     cartesian_topology.topology)
    if (me.rank == 0):
        if (testme(result_g, cartesian_topology)):
            print("Result is correct.")
        else:
            print("Result is incorrect!")
    return result_g, local_array

results=main()
results.wait()
results.display_outputs()
