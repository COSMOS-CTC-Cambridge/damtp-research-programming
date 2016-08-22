#!/usr/bin/env python

# try to use ipyparallel if available, fall back to direct MPI if not; note that there are
# two survivable failure modes: IOError, which means ipyparallel.Client() failed, and
# ImportError which means ipyparallel could not be inmported: in both these cases we can
# fall back to direct MPI (which may fail later, but that is another story)
try:
    import ipyparallel
    c = ipyparallel.Client(profile="mpi")
    directview=c[:]
    directview.block=True
except IOError:
    try:
        del ipyparallel
    except:
        pass
    import mpi4py
    from mpi4py import MPI
except ImportError:
    try:
        del ipyparallel
    except:
        pass
    import mpi4py
    from mpi4py import MPI

# import either in sync with ipyparallel remotes or just direct mpi. This is where the
# direct MPI mode fails if it is not available; lack of numpy is also fatal
try:
    with directview.sync_imports():
        import numpy
        import mpi4py
        from mpi4py import MPI
except NameError:
    import numpy
    import mpi4py
    from mpi4py import MPI
    class directview_class(object):
        '''Dummy class for direct MPI mode'''
        def __setitem__(self, name, value):
            setattr(self, name, value)
        def __getitem__(self, name):
            return getattr(self, name)
        def parallel(self, block=True):
            def passthrough(func):
                def callit(*args, **kwargs):
                    return func(*args, **kwargs)
                return callit
            return passthrough
        def remote(self, block=True):
            def passthrough(func):
                def callit(*args, **kwargs):
                    return func(*args, **kwargs)
                return callit
            return passthrough
        def apply_async(self, func, *args, **kwargs):
            return func(*args, **kwargs)
    directview=directview_class()


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
directview["topology"]=topology

class ghost_data(object):
    def __init__(self, topology, sizes):
        mx,my,mz = sizes
        Zds,Zdr,Zus,Zur=MPI.DOUBLE.Create_subarray(sizes, [mx,my,1], [0,0,1]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,my,1], [0,0,mz-1]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,my,1], [0,0,mz-2]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,my,1], [0,0,0]).Commit()
        Yds,Ydr,Yus,Yur=MPI.DOUBLE.Create_subarray(sizes, [mx,1,mz], [0,1,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,1,mz], [0,my-1,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,1,mz], [0,my-2,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [mx,1,mz], [0,0,0]).Commit()
        Xds,Xdr,Xus,Xur=MPI.DOUBLE.Create_subarray(sizes, [1,my,mz], [1,0,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [1,my,mz], [mx-1,0,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [1,my,mz], [mx-2,0,0]).Commit(), MPI.DOUBLE.Create_subarray(sizes, [1,my,mz], [0,0,0]).Commit()
        # Note: "down" and "up" refer to data movingg "downwards" and "upwards", so if one
        # rank sends data "down", that data is then moving "downwards" and must be
        # received by another rank with "down" argument as well
        self.types = {"X": {"send": {"down": Xds, "up": Xus}, "recv": {"down": Xdr, "up": Xur}},
                       "Y": {"send": {"down": Yds, "up": Yus}, "recv": {"down": Ydr, "up": Yur}},
                       "Z": {"send": {"down": Zds, "up": Zus}, "recv": {"down": Zdr, "up": Zur}}}
        self.axes = {"X": {"up":   {"dest": topology.up,    "source": topology.down},
                            "down": {"dest": topology.down,  "source": topology.up}},
                      "Y": {"up":   {"dest": topology.back,  "source": topology.front},
                            "down": {"dest": topology.front, "source": topology.back}},
                      "Z": {"up":   {"dest": topology.right, "source": topology.left},
                            "down": {"dest": topology.left,  "source": topology.right}}
        }
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

def initialise_values(me):
    local_array = numpy.zeros(numpy.array(me.localsizes).prod()).reshape(me.localsizes)
    sw = me.stencil_width
    local_array[sw:-sw,sw:-sw,sw:-sw]=((numpy.arange((numpy.array(me.localsizes)-2*sw).prod())+me.rank)**2).reshape(numpy.array(me.localsizes)-2*sw)
    return local_array
directview["initialise_values"]=initialise_values

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
directview["find_max_grad"]=find_max_grad

def testme(maxgrad, topology):
    size=topology.topology.Get_size()
    rank=topology.topology.Get_rank()
    expected=[1568,1600,1640,1680,1720,1760,1800,1840]
    return maxgrad == expected[size-1]
directview["testme"]=testme

@directview.remote(block=False)
def main():
    me=rankinfo(sizes=[3,4,5])
    cartesian_topology=topology(me)
    ghosts = ghost_data(cartesian_topology, me.localsizes)
    cartesian_topology.print_info()
    local_array = initialise_values(me)
    result_l, result_g = find_max_grad(cartesian_topology, local_array, ghosts)
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
try:
    results.wait()
    results.display_outputs()
except:
    pass

