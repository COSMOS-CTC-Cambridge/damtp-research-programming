Efficient and portable I/O
==========================

-   You will eventually want to read and write data, too, so
-   **Badly implemented I/O can easily take 99% of your run-time!**

Portable I/O
------------

-   some file formats will be hard or impossible to open on another computer so
-   avoid machine dependent I/O, like
    -   Fortran's `OPEN(UNIT ` 10, FORM = ’unformatted’, FILE = filename)=
        -   unlikely to be efficient
        -   likely to be very hard to open on another machine or Fortran library
    -   C's `fwrite(data, size, count, file)`
        -   with the right `size` and `count` this can be very efficient for a single-threaded application
        -   but not very portable: few data types are guaranteed to be equivalent across machines and bit-order can also change
-   some good libraries to portable I/O
    -   HDF5 is de facto high-performance data format and very standardised
    -   netcdf4 is also quite efficient (in fact it's hdf5 underneath)
    -   sometimes numpy's `save`, `savez` and `savez_compressed` are ok
        -   remember to pass `allow_pickle=False` to maintain portability

Performant I/O
--------------

-   all the above formats can be internally and transparently compressed and it's nearly always a good idea
    -   CPU time spent compressing is often more than saved in reduced time writing/reading to disc
    -   not to mention less disc space needed
    -   but compression is not magic:

``` {.python}
  import numpy
  import tempfile
  import cProfile
  import pstats
  data=numpy.random.random((1000,1000,100))
  tempfiles = [tempfile.TemporaryFile(dir=".") for i in [0,1,2,3]]
  cps = [cProfile.Profile() for i in range(len(tempfiles))]
  runs = ["numpy.savez", "numpy.savez_compressed", "numpy.savez_compressed", "numpy.savez_compressed"]
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
    -   unfortunately, python is not very good at demonstrating this but you can try to compile and run this

``` {.c}
  #define _GNU_SOURCE 1
  #define _POSIX_C_SOURCE 200809L
  #define _XOPEN_SOURCE 700
  #include <stdio.h>
  #include <stdlib.h>
  #include <unistd.h>
  #include <time.h>
  #include <sys/types.h>
  #include <sys/stat.h>
  #include <fcntl.h>


  #define SIZE 1000*1000*100

  int main(int argc, char *argv[]) {
    if (argc != 3)
      return 1;
    int fd1 = open(argv[1], O_WRONLY, O_DIRECT|O_TRUNC);
    int fd2 = open(argv[2], O_WRONLY, O_DIRECT|O_TRUNC);
    double *data = (void *) calloc(SIZE, sizeof(double));
    struct timespec t1, t2, t3;
    clock_gettime(CLOCK_MONOTONIC, &t1);
    for (int i=0; i<SIZE; i++) {
      write(fd1, data+i, sizeof(double)*1);
    }
    clock_gettime(CLOCK_MONOTONIC, &t2);
    write(fd2, data, sizeof(double)*SIZE);
    clock_gettime(CLOCK_MONOTONIC, &t3);
    printf("Writing one element at a time took %6li seconds\n", t2.tv_sec-t1.tv_sec);
    printf("Writing all elements at once took  %6li seconds\n", t3.tv_sec-t2.tv_sec);
    return 0;
  }
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
    -   needs a bit of a learning curve, unless you chose to use PETSc:

``` {.python}
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

  dm = PETSc.DMDA().create(dim=3, sizes = (-11,-7,-5), proc_sizes=(PETSc.DECIDE,)*3,
                           boundary_type=(PETSc.DMDA.BoundaryType.GHOSTED,)*3, stencil_type=PETSc.DMDA.StencilType.BOX,
                           stencil_width = 1, dof = 1, comm = PETSc.COMM_WORLD, setup = False)
  dm.setFromOptions()
  dm.setUp()
  vec1 = dm.createGlobalVector()
  vec1.setName("NameOfMyHDF5Dataset")
  vec2 = vec1.duplicate()
  vec2.setName("NameOfMyHDF5Dataset")
  fn = tempfile.NamedTemporaryFile()
```

-   that's just preamble, nothing new there, now we save `vec1` into a file

``` {.python}
  vwr=PETSc.Viewer().createHDF5(fn.name, mode=PETSc.Viewer.Mode.WRITE)
  vec1.view(vwr)
  vwr.destroy()
```

-   and then we load it into another vector

``` {.python}
  vwr=PETSc.Viewer().createHDF5(fn.name, mode=PETSc.Viewer.Mode.READ)
  vec2.load(vwr)
  print("Are they equal? " + str(bool(vec1.equal(vec2))))
```

-   if you run this in parallel using parallel HDF5 library, you just got all the hard bits for free
-   performance might still be bad, because

Know your filesystem
--------------------

-   typical HPDA/HPC system will have a high bandwith, high latency parallel file system where big files should go
-   most common is Lustre
    -   one often needs to set up a special directory on Lustre for very high bandwidth operations
    -   files are *striped* onto different pieces of hardware (OSTs) to increase bandwidth
    -   can be tricky as both the number of active OSTs and number of writers in code affect the bandwidth
-   on COSMOS the filesystem is CXFS, which is not like Lustre
    -   no performance benefit from single-file parallel I/O
    -   multi-file parallel I/O is better
    -   for Lustre users our CXFS has fixed stripe of 2

Checkpointing
-------------

-   Your code should be able to do this on its own to support solving the problem by running the code several times: often not possible to obtain access to a computer for long enough to solve in one go.
-   Basically, you save your iterate (current best estimate solution) and later load it from file instead of using random or hard coded initial conditions.
-   Parallel Visualisation: ParaView

Technical problems… Let's see if I can show something on my laptop
