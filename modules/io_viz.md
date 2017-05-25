Efficient and portable I/O
==========================

-   You will eventually want to read and write data, too, so
-   **Badly implemented I/O can easily take 99% of your run-time!**

Portable I/O
------------

-   plain text is portable, but
    -   horribly space wasting (unless compressed, which then harms portability)
    -   horribly slow as everything needs to be converted
        -   unless your actual calculations are done using letters
    -   cannot really be parallelised so in parallel even more slower
-   some file formats will be hard or impossible to open on another computer so
-   avoid machine dependent I/O, like
    -   The unformatted IO in Fortran
        -   unlikely to be efficient unless every rank writes their own file
        -   likely to be very hard to open on another machine or Fortran library
    -   C's `fwrite(data, size, count, file)`
        -   with the right `size` and `count` this can be very efficient for a single-threaded application but again requires each rank to write its own file to be efficient in parallel applications
        -   but not very portable: few data types are guaranteed to be equivalent across machines and bit-order can also change
-   some good libraries to portable I/O
    -   HDF5 is de facto high-performance data format and very standardised
    -   netcdf4 is also quite efficient (in fact it's HDF5 underneath)
    -   sometimes numpy's `save`, `savez` and `savez_compressed` are ok
        -   remember to pass `allow_pickle=False` to maintain portability

Performant I/O
--------------

-   HDF5, netcdf, and the numpy formats can all be internally and transparently compressed
    -   CPU time spent compressing is often more than saved in reduced time writing/reading to disc
    -   not to mention less disc space needed
    -   may sound like a time-saver but compression is not magic:

``` python
import numpy
import tempfile
import cProfile
import pstats
data=numpy.random.random((1000,1000,100))
tempfiles = [tempfile.TemporaryFile(dir=".") for i in [0,1,2,3]]
cps = [cProfile.Profile() for i in range(len(tempfiles))]
runs = ["numpy.savez", "numpy.savez_compressed", "numpy.savez_compressed",
        "numpy.savez_compressed"]
for i,r in enumerate(runs):
    if (i==2):
        data[100:900,100:900,30:70]=0.0
    if (i==3):
        data = numpy.ones((1000,1000,100), dtype=numpy.float64)
    cps[i].runcall(eval(r), tempfiles[i], {"array_called_data":data})

print('''Time spent and file sizes:
  uncompressed random data:   {uncompt:g}\t{uncomps} 
  compressed random data:     {compt:g}\t{comps}
  compressed semirandom data: {semit:g}\t{semis}
  compressed zeros:           {zerot:g}\t{zeros}'''.format(
      uncomps=tempfiles[0].tell(),
      comps=tempfiles[1].tell(),
      semis=tempfiles[2].tell(),
      zeros=tempfiles[3].tell(),
      uncompt=pstats.Stats(cps[0]).total_tt,
      compt=pstats.Stats(cps[1]).total_tt,
      semit=pstats.Stats(cps[2]).total_tt,
      zerot=pstats.Stats(cps[3]).total_tt
  ))
```

-   floating point numbers are often almost random from a compression algorithm's point of view
-   HDF5's `szip` algorithm is supposed to understand floating point numbers and compress smartly
-   **always write huge chunks of data**
    -   latency is more likely to ruin performance than anything else, so unless you know exactly where the I/O bottleneck is, do big writes into big files, even buffering internally in your code if necessary
    -   and big writes really means big: a 10 MB write is not a big write, let alone a big file!
    -   unfortunately, python is not very good at demonstrating this but you can try to compile and run this (available in `codes/cpp/chunk_size_effect.c`)

``` python
%%bash
cat ../codes/cpp/chunk_size_effect.c
mpicxx -o ../codes/cpp/chunk_size_effect ../codes/cpp/chunk_size_effect.c
f1=$(mktemp ./testXXXXXXXX)
f2=$(mktemp ./testXXXXXXXX)
../codes/cpp/chunk_size_effect $f1 $f2
rm $f1 $f2
```

-   Bit of a dark magic as disc, unlike the CPU, is a shared resource: other users use same discs

Parallel I/O
------------

-   always use parallel I/O for parallel programs
-   poor man's parallel I/O
    -   every worker writes its own file
    -   can be the fastest solution
    -   but how do you use those files with different number of workers for e.g. post-processing?
-   MPI I/O or MPI-enabled HDF5 library deal with that
    -   they can write a single file simultaneously from all workers
    -   may do some hardware-based optimisations behind the scenes
    -   can also map the writes to the MPI topology
    -   needs a bit of a learning curve, unless you chose to use PETSc or h5py:

``` python
from __future__ import division
import sys
import time
import numpy
import mpi4py
from mpi4py import MPI
import petsc4py
petsc4py.init(sys.argv)
from petsc4py import PETSc
import tempfile

dm = PETSc.DMDA().create(dim=3, sizes = (-11,-7,-5),
                         proc_sizes=(PETSc.DECIDE,)*3,
                         boundary_type=(PETSc.DMDA.BoundaryType.GHOSTED,)*3,
                         stencil_type=PETSc.DMDA.StencilType.BOX,
                         stencil_width = 1, dof = 1, comm =
                         PETSc.COMM_WORLD, setup = False)
dm.setFromOptions()
dm.setUp()
vec1 = dm.createGlobalVector()
vec1.setName("NameOfMyHDF5Dataset")
vec2 = vec1.duplicate()
vec2.setName("NameOfMyHDF5Dataset")
fn = tempfile.NamedTemporaryFile()
```

-   that's just a preamble, nothing new there, now we save `vec1` into a file

``` python
vwr=PETSc.Viewer().createHDF5(fn.name, mode=PETSc.Viewer.Mode.WRITE)
vec1.view(vwr)
vwr.destroy()
```

-   and then we load it into another vector

``` python
vwr=PETSc.Viewer().createHDF5(fn.name, mode=PETSc.Viewer.Mode.READ)
vec2.load(vwr)
```

-   and check we got the same stuff back

``` python
print("Are they equal? " + ["No!", "Yes!"][vec1.equal(vec2)])
```

-   if you run this in parallel using parallel HDF5 library, you just got all the hard bits for free
-   and a similar example in `h5py`
-   note that running this in the frontend uses just one rank

``` python
import mpi4py
from mpi4py import MPI
import h5py
import tempfile
import os
import array
if (MPI.COMM_WORLD.rank == 0):
    temp="hdf5_visualisation_example.h5"
    temp2=array.array("c","")
    temp2.fromstring(temp)
else:
    temp2=array.array("c", "\0")*1024
MPI.COMM_WORLD.Bcast([temp2, MPI.CHAR], root=0)   
KEEP_ME_AROUND = temp2.tostring()
rank = MPI.COMM_WORLD.rank
print KEEP_ME_AROUND                                                  
f = h5py.File(KEEP_ME_AROUND, "w", driver="mpio", comm=MPI.COMM_WORLD)
dset = f.create_dataset("test", (4,), dtype="f8")
dset[rank] = rank
f.close()
```

``` python
%%bash
mpirun -np 4 python ../codes/python/parallel_io_h5py.py
```

-   performance might still be bad, because

Know your filesystem
--------------------

-   typical HPDA/HPC system will have a high bandwith, high latency parallel file system where big files should go
-   most common is Lustre
    -   one often needs to set up a special directory on Lustre for very high bandwidth operations
    -   files are *striped* onto different pieces of hardware (OSTs) to increase bandwidth
    -   can be tricky as both the number of active OSTs and number of writers in code affect the bandwidth
-   on machines like COSMOS the filesystem is CXFS, which is not like Lustre
    -   no performance benefit from single-file parallel I/O
    -   multi-file parallel I/O is better
    -   for Lustre users our CXFS has fixed stripe of 2

Checkpointing
-------------

-   Your code should be able to do this on its own to support solving the problem by running the code several times: often not possible to obtain access to a computer for long enough to solve in one go.
-   Basically, you save your iterate or current best estimate solution and later load it from file instead of using random or hard coded initial conditions.

Simple Visualisation
====================

matplotlib
----------

-   The `matplotlib` python package is terribly good but cannot do Big Data as it is **not** distributed
    -   has extensive documentation at [matplotlib homepage](http://matplotlib.org/contents.html)
-   It's also not properly parallel so it can often be slow
-   But it is
    -   easy
    -   interactive
    -   if you only need to plot a subset of your data (e.g. 2D slice of 3D data) it might scale well enough
-   please note that interactivity over the network will be laggy; we show how it works anyway
-   the following "ipython magic" is only needed to embed the output in the ipython/jupyter notebook
    -   it needs to be done *once* per python session, so please always execute this cell even if you only want to look at a single later example

``` python
%matplotlib notebook
```

### A Simple Example: a parabola

<span id="pylab_plot_example_export"></span>

``` python
import pylab, numpy
x = numpy.mgrid[-5:5:100j]
pylab.plot(x, x**2, "b-", label=r"$x^2$")
pylab.legend()
```

### Plotting a Saved File: a simple 3D example

-   in this example we use the file we created earlier: `../files/genfromtxt_example_data.txt` and save it to another called `../files/genfromtxt_example_data.png`

``` python
infile = "../files/genfromtxt_example_data.txt"
oufile = "../files/genfromtxt_example_plot.png"
import numpy
import matplotlib
import matplotlib.pyplot
from mpl_toolkits.mplot3d import Axes3D

def randrange(n, vmin, vmax):
    return (vmax - vmin)*numpy.random.rand(n) + vmin

data = numpy.genfromtxt(infile, comments="#", delimiter="\t", skip_header=3)
fig = matplotlib.pyplot.figure()
ax = fig.add_subplot(111, projection='3d')
n = data.shape[0]
# plot a sphere for each particle
# colour charged particles red (charge>0), blue (charge<0) and neutrals green
blues = data[data[:,7]<0]
reds = data[data[:,7]>0]
greens=data[numpy.logical_not(numpy.logical_or(data[:,7]<0,data[:,7]>0))]
ax.scatter(blues[:,0], blues[:,1], blues[:,2], c="b", edgecolors="face",
           marker="o", s=blues[:,6])
ax.scatter(reds[:,0], reds[:,1], reds[:,2], c="r", edgecolors="face",
           marker="o", s=greens[:,6])
ax.scatter(greens[:,0], greens[:,1], greens[:,2], c="g", edgecolors="face",
           marker="o", s=greens[:,6])
ax.quiver(blues[:,0], blues[:,1], blues[:,2], blues[:,3], blues[:,4],
          blues[:,5], pivot="tail")
ax.quiver(reds[:,0], reds[:,1], reds[:,2], reds[:,3], reds[:,4],
          reds[:,5], pivot="middle")
ax.quiver(greens[:,0], greens[:,1], greens[:,2], greens[:,3], greens[:,4],
          greens[:,5], pivot="tip")
ax.set_xlabel('X Label')
ax.set_ylabel('Y Label')
ax.set_zlabel('Z Label')
matplotlib.pyplot.savefig(oufile)
print(oufile, end="")
```

### Advanced Features

-   we did not use anything advanced, except matplotlib's builtin latex capability, but it provides a full control of the whole canvas and image window

### Animation Using matplotlib

-   matplotlib has a rudimentary animation capability as well
    -   ParaView is better in this, and matplotlib will not be able to create beautiful complex animations
    -   but it can do simple ones
    -   and it can be used to generate lots of frames for a video
        -   but unless you use matplotlib-frontend specific, just using file-write backend directly, without plotting on screen is much faster
        -   in both cases you can convert to video like

            ``` example
            ffmpeg -f image2 -pattern_type glob -framerate 25 -i\
             'testanimationsaveframe_*.png' -s 800x600 foo.mkv
            ```

    -   or illustrate how an algorithm works, see exercises!
-   here's an example with all the important bits:

``` python
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
plt.ion()

def data_gen(t=0):
    '''A generator function, which must use "yield" as all generators do,
    to produce results one frame at a time. In this example, the "run"
    function will actually remember/save data for previous frames so
    we get away with generating just the new data. Whatever we return
    will be passed as the sole argument to "run".'''
    cnt = 0
    while cnt < 1000:
        cnt += 1
        t += 0.1
        yield t, np.sin(2*np.pi*t) * np.exp(-t/10.)

def init():
    '''A setup function, called before the animation begins.'''
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlim(0, 100)
    del xdata[:]
    del ydata[:]
    line.set_data(xdata, ydata)
    return line,

fig, ax = plt.subplots()
line, = ax.plot([], [], lw=2)
ax.grid()
xdata, ydata = [], []

def run(data, args):
    '''This is called by the animator for each frame with new data from
    "data_gen" each time. What we do here is up to us: we could even
    write the plot to disc (see the commented-out line) or we could do
    something completely unrelated to matplotlib!  The present code
    will append new data to its old (global variable) data and
    generate a new animation frame. Note that matplotlib holds a copy
    of our old data so we could fish it out from the depths of its
    internal representation and append to that but that's a bit
    complicated for our example here.  We have been passed "args" but
    we ignore that.'''
    t, y = data
    xdata.append(t)
    ydata.append(y)
    xmin, xmax = ax.get_xlim()
    if t >= xmax:
        ax.set_xlim(xmin, 2*xmax)
        ax.figure.canvas.draw()
    line.set_data(xdata, ydata)
    return line,

ani = animation.FuncAnimation(fig, run, data_gen, blit=False, interval=10, 
                              fargs=("arguments",), repeat=False, init_func=init)
plt.show()
```

Exercise
--------

Use your earlier Game of Life or Random Walker code and animate it using `FuncAnimation`. You have already written the stepper in such a way that it is easy to wrap into a small "run" function which generates frames one at a time. Hint: easiest way to plot is probably matplotlib's `imshow` function.

### Solution

A demonstration of how to animate a Game of Life is Available in the repo. If your Random Walker has the same signature, you could animate it with the demonstrator, too.

Parallel Visualisation: ParaView (very quick intro)
===================================================

-   ParaView, as the name suggests, runs in (distributed) parallel: no data is too big if you managed to create it in the first place
-   Some complications in getting the proper distributed parallel version up and running:
    -   ParaView is split into a client and a server
    -   normal `paraview` command runs client with a local server, but not in parallel
    -   not what you want anyway: you can run ParaView this way on your supercomputer, but the UI will be **very** slow as all plotting data and interaction need to go over the network
    -   you need to run `pvserver` on the "big" machine and connect `paraview` frontend to that
    -   so far so simple, but `paraview` needs to be able to connect to `pvserver` and this is usually blocked by a firewall
    -   need to punch a hole to the firewall in a three step process:
        -   `ssh` to the machine you want to run `pvserver` on and start `pvserver`
        -   from `pvserver`'s output, find the port it listens on (`Connection URL:`); it will look like `cs://vega:11111`
        -   now punch a hole in firewall with `ssh -NL 11111:localhost:PortYouJustFound PVServerMachineName`
        -   then start `paraview` locally and connect it to the local server at port `11111`
        -   not really paraview's fault here: blame the criminals whose activities enforce everyone to firewall off their computers

A simple example with HDF5 without remote `pvserver`
----------------------------------------------------

-   first we write the HDF5 file using `h5py`, one of the many python HDF5 interfaces

``` python
import numpy
import tempfile
import h5py
import os
file=tempfile.NamedTemporaryFile(
    dir=os.path.join("..","files"),
    prefix="hdf5_visualisation_example",
    suffix=".h5",
    delete=False)
file.close()
xmin, xmax, ymin, ymax, zmin, zmax = -5,+5,-5,+5,-5,+5
xpts, ypts, zpts = 101, 101, 101
cutoff1, cutoff2, cutoff3 = 1.0, 3.0, 4.0
dsname="mydataset"
m = numpy.mgrid[xmin:xmax:xpts*1j,ymin:ymax:ypts*1j,zmin:zmax:xpts*1j]
r = (m**2).sum(axis=0)**0.5
mydata = cutoff2/(cutoff2-cutoff3)**2*(r-cutoff3)**2
mydata[r<cutoff2] = r[r<cutoff2]
mydata[r<cutoff1] = 0.0
mydata[r>cutoff3] = 0.0
h5file = h5py.File(file.name,"w")
h5file.create_dataset(dsname, data=mydata)
print("Wrote data to file {f}.".format(f=file.name))
```

-   note that we did not close the file yet
-   but HDF5 is too generic for paraview to have a generic import module, we need to tell paraview what the HDF5 file looks like
    -   do not ask me why this information cannot be in the file itself
-   note the numpy-like access to the dataset in the HDF5 file

``` python
str="""<?xml version="1.0" ?>
<!DOCTYPE Xdmf SYSTEM "Xdmf.dtd" []>
<Xdmf Version="2.0">
  <Domain>
    <Grid Name="{meshname}" GridType="Uniform">
      <Topology TopologyType="3DCoRectMesh" NumberOfElements="{Nx} {Ny} {Nz}"/>
       <Geometry GeometryType="ORIGIN_DXDYDZ">
        <DataItem DataType="Float" Dimensions="3" Format="XML">
          {xmin} {ymin} {zmin}
        </DataItem>
        <DataItem DataType="Float" Dimensions="3" Format="XML">
          {dx} {dy} {dz}
        </DataItem>
      </Geometry>
      <Attribute Name="mydata" AttributeType="Scalar" Center="Node">
        <DataItem Dimensions="{Nx} {Ny} {Nz}" NumberType="Float"
         Precision="{precision}" Format="HDF">
          {filename}:/{datasetname}
        </DataItem>
      </Attribute>
    </Grid>
  </Domain>
</Xdmf>
""".format(meshname="mymesh",
           Nx=h5file[dsname].shape[0], Ny=h5file[dsname].shape[1],
           Nz=h5file[dsname].shape[2],
           xmin=xmin, ymin=ymin, zmin=zmin,
           dx=(xmax-xmin)*1.0/(xpts-1), dy=(ymax-ymin)*1.0/(ypts-1),
           dz=(zmax-zmin)*1.0/(zpts-1),
           precision=h5file[dsname].dtype.itemsize,
           filename=h5file.filename,
           datasetname=dsname)
xdmffilen=h5file.filename.replace(".h5",".xdmf")
xdmffile=open(xdmffilen,"w")
xdmffile.write(str)
xdmffile.close()
h5file.close()
```

-   now to paraview which we unfortunately cannot do in Jupyter
