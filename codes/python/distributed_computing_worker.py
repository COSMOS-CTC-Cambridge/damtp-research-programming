import numpy
import mpi4py
from mpi4py import MPI

# neutralise the directview assignments and decorators
import directview
directview = directview.directview_class()
try:
    if (directview):
        pass
except:
    import ipyparallel
    c = ipyparallel.Client(profile="mpi_slurm", cluster_id="Azure_cluster_0")
    directview=c[:]
    directview.block=True
    with directview.sync_imports():
        import numpy
        import mpi4py
        from mpi4py import MPI

class rankinfo(object):
    '''This holds a few "global" values of our problem,
    like stencil width and problem size.

    Parameters
    ----------

    sizes : tuple of numbers of lattice points without ghost
            points along the coordinate axes (in x,y,z order)

    Attributes
    ----------

    rank : the rank of this class in MPI.COMM_WORLD
    size : the number of ranks in  MPI.COMM_WORLD
    ndim : how many physical dimensions does our lattice have
    periods : periodicity of the lattice
    stencil_width : the number of ghost points needed from
                    outside of the lattice on each side
    localsizes : the number of lattice points along the
                 coordinate axes including the ghost points
    '''
    def __init__(self, sizes):
        '''See above for details of initialisation.'''
        self.ndim=3
        self.periods=[False, True, True]
        self.stencil_width = 1
        self.rank=MPI.COMM_WORLD.Get_rank()
        self.size=MPI.COMM_WORLD.Get_size()
        self.localsizes=[x+self.stencil_width*2 for x in sizes]
directview["rankinfo"]=rankinfo

def serialised_print(msg, topo):
    '''Print out a message from every rank syncronously in rank-order.
    Barrier() is global, so every rank must call it or we deadlock.'''
    myrank = topo.Get_rank()
    for rankid in range(0,topo.Get_size()):
        if (myrank == rankid):
            print(msg)
        topo.Barrier()
    return
directview["serialised_print"]=serialised_print

class topology(object):
    '''This class holds information related to the topology of the MPI
    Cartesian Topology

    Compute_dims() is used to find the most similar siez factors of
    "self.me.size" to distribute the data and subsequently Create_cart()
    actually creates the cartesian topology communicator. This is one of
    the most useful and important MPI calls. The parameter reorder=True
    means the MPI libarary is allowed to give the ranks in the new
    communicator different numbers than in the old one. This allows the
    library to optimise communications between ranks, assuming most
    communication is nearest-neighbour (and if it is not, using a
    Cartesian topology is probably pointless). Finally, Shift() calls
    are used to find who those neighbours are.

    '''
    def __init__(self, rankinfo):
        '''Find out the best distribution of the lattice amonst the ranks of the
        communicator passed inside "rankinfo", create the topology, and
        save information about the neighbours of present rank.

        Parameters
        ----------
        rankinfo : a rankinfo instance describing current communicator

        Attributes
        ----------
        dims : dimensions of the cartesian MPI rank grid (not lattice!)
        topology : the new cartesian topology communicator
        shifts : a dict of dicts of which rank to talk to when going
                 along "X", "Y", or "Z" direcion in "up" or "down"
                 direction

        '''
        self.me=rankinfo
        self.dims=MPI.Compute_dims(self.me.size, self.me.ndim)
        self.topology=MPI.COMM_WORLD.Create_cart(self.dims,
                                                 periods=self.me.periods, reorder=True)
        left,right = self.topology.Shift(0,1)
        front,back = self.topology.Shift(1,1)
        up,down = self.topology.Shift(2,1)
        self.shifts={"X": {"up": up, "down": down},
                     "Y": {"up": back, "down": front},
                     "Z": {"up": right, "down": left}}
    def print_info(self):
        '''Print out textual information of the cartesian topology'''
        coords = self.topology.Get_coords(self.me.rank)
        msg="I am rank {rank} and I live at {coords}.".format(
            rank=self.me.rank, coords=coords)
        msg = msg + "Inverse lookup of {coords} gives rank {rank}.".format(
            coords=coords,rank=self.topology.Get_cart_rank(coords))
        serialised_print(msg, self.topology)
directview["topology"]=topology

class ghost_data(object):
    '''Ghost communication manager object.

    Basically consists of 12 MPI datatype instances describing the ghost
    send/recv (2) communications in up/down (*2) the three (*3=12)
    dimensions.

    Parameters
    ----------
    topology : a topology instance containing the desired cartesian
               communicator
    sizes : the size of the lattice on this rank (including ghost cells)

    Attributes
    ----------
    types : a dict of dicts of dicts containing instances of the 12
            datatypes; outermost dict keys are axis names, next level
            keys are "send" or "recv" and last level is direction "up"
            or "down"   
    axes : dict of dicts containing the neighbours along the axes; outer
           dict is keyed with axis names, inner dict is keyed with
           direction "up" or "down"
    mx, my, mz : numbers of lattice points along the axes, including
                 ghost points

    Methods
    -------
    None supposed to be called from outside the class.

    '''
    def __init__(self, topology, sizes):
        '''Use MPI.DOUBLE.Create_subarray to create the datatypes required for
        ghost communications. We use MPI.DOUBLE as the underlying unit
        datatype element as our data is of that type.

        The call to Create_subarray() has three arguments
            - the first, sizes, is the (local) size of the full 3D array
              of elements of the basal type
            - the second argument is the size and shape of the subarray:
              this needs to be of the same dimension as the full array,
              but one dimension can be just 1 grid point deep as we do
              here, effectively making it one dimension lower
            - the third argument specifies the grid point where the
              subarray starts, in coordinates of the full local array

        '''
        self.mz,self.my,self.mx = sizes
        self.types = {}
        self.axes = {}
        for axis in ["X", "Y", "Z"]:
            self.types[axis]={}
            self.axes[axis]={}
            for op in ["send", "recv"]:
                self.types[axis][op]={}
                for movements in [("up","down"), ("down","up")]:
                    movement, negmovement = movements
                    self.types[axis][op][movement] = MPI.DOUBLE.Create_subarray(
                        sizes, self.get_plaq(axis),
                        self.get_corner(axis,op,movement))
                    self.types[axis][op][movement].Commit()
                    self.axes[axis][movement]={
                        "dest": topology.shifts[axis][movement],
                        "source": topology.shifts[axis][negmovement]}
    def axis2basisvec(self, axis):
        return numpy.array([axis == "Z", axis == "Y", axis == "X"],
                           dtype=numpy.float64)
    def get_plaq(self, axis):
        vec = self.axis2basisvec(axis)
        pl = [self.mz, self.my, self.mx]*(1-vec)+vec
        return list(pl)
    def get_corner(self, axis, sendrecv, movement):
        vec = self.axis2basisvec(axis)
        axis_size = [x[0] for x in ((self.mx, "X"), (self.my, "Y"),
                                    (self.mz, "Z")) if x[1]==axis][0]
        loc = vec*( (movement=="down") +
                    ((sendrecv=="send")*(movement=="up") or
                     (sendrecv=="recv")*(movement=="down"))*(axis_size-2)
        )
        return list(loc)
directview["ghost_data"]=ghost_data

def ghost_exchange_start(topo, localarray, ghostdefs):
    '''Start sending and receiving the ghost data.

    Parameters
    ----------
    topo : the communicator to use
    localarray : the numpy array to read/write
    ghostdefs : an instance of ghost_data of this particular lattice and
                topology

    Returns
    -------
    commslist : a list of the MPI communication objects that control the
                transfers we started
    '''    
    commslist=[]
    for axis in ["X", "Y", "Z"]:
        for direction in ["up", "down"]:
            commslist.append(
                topo.topology.Irecv(
                    buf=[localarray, 1,
                         ghostdefs.types[axis]["recv"][direction]],
                    source=ghostdefs.axes[axis][direction]["source"],
                    tag=0))
    for axis in ["X", "Y", "Z"]:
        for direction in ["up", "down"]:
            commslist.append(
                topo.topology.Isend(
                    buf=[localarray, 1,
                         ghostdefs.types[axis]["send"][direction]],
                    dest=ghostdefs.axes[axis][direction]["dest"],
                    tag=0))
    return commslist
directview["ghost_exchange_start"]=ghost_exchange_start

def ghost_exchange_finish(commslist):
    '''Wait until all the MPI transfers in "commslist" have finished.

    Parameters
    ----------
    commslist : list of transfers to wait for
    '''
    MPI.Request.Waitall(commslist)
    return
directview["ghost_exchange_finish"]=ghost_exchange_finish

def initialise_values(me, topo):
    '''Set up the initial values in the lattice; never mind the details,
       they are "problem" dependent anyway.

    Parameters
    ----------
    me : an instance of rankinfo
    topo : an instance of topology; should be the same Cartesian
           topology we create earlier using "me"

    Return
    ------
    local_array : the local portion of the global data as initialised
                  (with ghost points, but ghosts are uninitialised)
    '''
    size = topo.topology.Get_size()
    local_array = numpy.zeros(me.localsizes)
    procsalong, periods, mycoord = topo.topology.Get_topo()
    mycorner = mycoord*(numpy.array(me.localsizes)-2)
    sz, sy, sx = numpy.array(me.localsizes)-2
    for z in range(sz):
        for y in range(sy):
            start = (mycorner[2] + sx*(y+mycorner[1])*procsalong[2] +
                     sy*sx*(z+mycorner[0])*procsalong[2]*procsalong[1])
            stop = start + sx
            local_array[z+1,y+1,1:-1] = numpy.arange(start,
                                                     stop, step=1)**2
    return local_array
directview["initialise_values"]=initialise_values


def compute_grad(topology, local_array, ghostdefs):
    '''Compute the 2nd order central finite difference gradient of the
    data.

    Parameters
    ----------
    topology : an instance of the relevan Cartesian topology
    local_array : the local portion of the global lattice, including
                  ghost points
    ghostdefs : the ghost data communication objects

    Return
    ------
    gradients : the gradient of the interior points of "local_array";
                note that numpy.gradient will compute values at the
                ghost points, too, but those are not included in
                "gradients" (note the slice)
    '''
    commslist=ghost_exchange_start(topology, local_array, ghostdefs)
    # could do work here but NOT use ghost points!
    ghost_exchange_finish(commslist)
    gradients=numpy.array(numpy.gradient(local_array))[:,1:-1,1:-1,1:-1]
    return gradients
directview["compute_grad"]=compute_grad

def find_global_max(topology, local_array, ghostdefs):
    '''Find the global maximum value on the lattice.  We first use the
    .max() method to find the local maximum Then use Allreduce to apply
    MPI.MAX operation (=find greatest) to all local values in one go
    inside MPI library.
    Finally Allreduce sends the result to all ranks: Reduce would give
    the result to one rank only.  N.B. There would be other operations
    we can do, too, like MPI.SUM.

    Parameters
    ----------
    topology : an instance of the relevant Cartesian topology
    local_array : the local portion of the global lattice data
    ghostdefs : the ghost transfer objects

    Returns
    -------
    maxgrad_local,maxgrad_global : local and global maximum on the
                                   lattice
    '''
    maxgrad_local = numpy.array(local_array).max()
    maxgrad_global = numpy.zeros_like(maxgrad_local)
    topology.topology.Allreduce([maxgrad_local, MPI.DOUBLE],
                                [maxgrad_global, MPI.DOUBLE],
                                op=MPI.MAX)
    return maxgrad_local, maxgrad_global
directview["find_global_max"]=find_global_max

def testme(maxgrad, topology, localsizes):
    '''Test if we get the correct result.

    Parameters
    ----------
    maxgrad : the computed result
    topology : an instance of the relevant Cartesian comunicator

    Return
    ------
    maxgrad == expected[size-1] : True if the computed "maxgrad" was
                                  correct, False if not
    '''
    size=topology.topology.Get_size()
    rank=topology.topology.Get_rank()
    procsalong, periods, mycoord = topology.topology.Get_topo()
    nz,ny,nx = procsalong
    sz,sy,sx = (numpy.array(localsizes)-2)*numpy.array([nz,ny,nx])
    maximum = 2*sx*sy*(-1+sx*sy*(sz-1))
    expected=maximum
    return maxgrad == expected
directview["testme"]=testme

@directview.remote(block=False)
def main():
    '''Main code: run the bits and pieces defined above with the relevant
    arguments for the demonstration 3x4x5 lattice. This is execured on
    the remote workers due to the decorator, so return values stay at
    the workers.

    Return
    ------
    result_g, local_array : the global maximum of the data, the local
                            portion of the array
    '''
    me=rankinfo(sizes=[3,4,5])
    cartesian_topology=topology(me)
    ghosts = ghost_data(cartesian_topology, me.localsizes)
    cartesian_topology.print_info()
    local_array = initialise_values(me, cartesian_topology)
    gradients = compute_grad(cartesian_topology, local_array, ghosts)
    result_l, result_g = find_global_max(cartesian_topology, gradients,
                                         ghosts)
    serialised_print(
        "Rank {rank} ".format(
            rank=me.rank)+
        "had max gradient {maxgrad_l} ".format(
            maxgrad_l=result_l)+
        "while the global was {maxgrad_g}.".format(
            maxgrad_g=result_g),
        cartesian_topology.topology)
    if (me.rank == 0):
        if (testme(result_g, cartesian_topology, me.localsizes)):
            print("Result is correct.")
        else:
            print("Result is incorrect!")
    return result_g, local_array
