Profiling
=========

-   You've got a well designed, parallel, scalable code, but it still takes way too long to run.
-   Please do use good programming practices as those will make optimising (and profiling) a lot easier

Profiling Your Code
-------------------

### First Look: Function Level Overview

-   Always find your "hot spots" before starting to optimise
    -   The hot spot is often not where you think it is
-   In Python, there is a built-in tool `cProfile` we can use
    -   For C/Fortran you can use TODO!!! URLS!!! HPCToolkit, TAU, or if you have Intel compatible hardware, Intel VTune
-   Example code initialises the data, computes the Laplacian, takes a Fourier Transform, adds a little to each variable, transforms back, and writes to disc

``` {.python}
  import numpy
  import scipy
  import scipy.fftpack 
  import cProfile
  import time as timemod
  import os

  def Init(sizes):
      return 

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

  def Fourier(data):
      return scipy.fftpack.fftn(data)

  def AddLittle(data):
      for ii in range(0,data.shape[0]):
          for jj in range(0,data.shape[1]):
              for kk in range(0,data.shape[2]):
                  data[ii,jj,kk] = data[ii,jj,kk] + 1./numpy.pi
      return

  def IFourier(data):
      return scipy.fftpack.ifftn(data)

  def WriteToFile(data):
      filename="ihopethisfiledoesnotexist.dat"
      data.tofile(filename, sep=" ")
      os.unlink(filename)
      return

  def RunProfile(size):
      variables = Init(size)
      Laplacian(variables["data"], variables["laplacian"], variables["lattice_spacing"])
      fftdata=Fourier(variables["data"])
      AddLittle(fftdata) # pass-by-reference, so OUR fftdata WILL CHANGE
      finaldata=IFourier(fftdata)
      WriteToFile(finaldata)

  SIZE=100
  cp=cProfile.Profile()
  start = timemod.clock()
  cp.runcall(RunProfile, SIZE)
  end = timemod.clock()
  print("cProfile gave total time of {time} s and the following profile.".format(time=end-start))
  cp.print_stats(sort="time")
```

-   that was a bit long, wasn't it?
    -   that code is intentionally *BAD*
    -   unfortunately we need it to be bad to see effects of our optimisation later on!
-   TODO!!! Laplacian, but err... compute intensify it?

### Second Look: Line Level Profile

-   So, `Laplacian` is our most time-consuming part of the code: how do we optimise it?
    -   the first step in this case will be easy but it will get harder as we proceed and
-   for larger routines you would like to have a line-by-line profile
    -   this is easy to do with C, C++ and Fortran: all the tools mentioned above can give a line-by-line profile
    -   not so for python: there is [line<sub>profiler</sub>](https://github.com/rkern/line_profiler) or [pprofile](https://github.com/vpelletier/pprofile) and a slightly different approach: [pyvmmonitor](http://www.pyvmmonitor.com/)
    -   some large routines can and perhaps should be split into smaller ones, thus removing the need to profile line-by-line

### Third Look: Hardware Utilisation

-   Digging even deeper, one may want to know why a particular code provides so few operations / second compared to what google says the CPU can do
-   Let's look what kind of performance our `Laplacian` achieves

``` {.python}
  import pstats
  p=pstats.Stats(cp)
  Ltime=[p.stats[x] for x in p.stats if x[2]=="Laplacian"][0][2]
  LGF=(SIZE-2)**3*17
  print("Laplacian executed in {time} at {GFps} GF/s".format(time=Ltime, GFps=LGF/Ltime/1e9))
```

-   One should also consider other hardware utilisation issues, like memory bandwidth and latency
    -   We'll have a look at some of those next

### Note

The profiler modules are designed to provide an execution profile for a given program, not for benchmarking purposes (for that, there is timeit for reasonably accurate results). This particularly applies to benchmarking Python code against C code: the profilers introduce overhead for Python code, but not for C-level functions, and so the C code would seem faster than any Python one.

Optimisation
============

What is good and what is bad
----------------------------

-   no good metric:
    -   a very optimised implementation of a bad algorithm may still be more time consuming than an unoptimised implementation of a good algorithm
    -   what to measure: GF/s, % peak, cache misses, ...?
-   still to some extent useful to measure e.g. %peak
    -   if near theoretical peak, no point in trying to optimise more
    -   anything over 20% peak in a kernel is good
    -   measuring GF/s can compare different implementations of the same algorithm (or your progress in optimising it)
        -   **pitfall**: GF can change with optimisations and especially with compiled languages you might not even know
-   eventually we are interested in the runtime, so that's a good measure of progress

Language Differences
--------------------

-   one often hears arguments about language A being faster than language B
    -   rubbish
    -   language A may be better suited than others for achieving good in problem X but there's no overall winner
-   another often repeated claim is interpreted languages are slow
    -   rubbish again
    -   well written python is actually quite optimal and not to be shied away from!
    -   python WILL CACHE intermediate results
        -   performance can fluctuate wildly if doing repetitive tasks, like gathering performance statistics
        -   performance analysis is hard as repeating the same computation will use the cache and doing just one iteration has natural variation and overheads
        -   can be alleviated by using relatively big problems
        -   can eat more memory than you think (but won't run out)
    -   main issue with python is *it cannot do OpenMP*
        -   but it has its own tools: *multiprocessing* and *handythread*, which works almost as
        -   python combined with *cython* can automatically generate (hopefully) fast C/C++ extensions which can then use OpenMP
        -   we'll have a look at cython later
    -   other solutions for python include
        -   `scipy.weave` which is a JIT solution and no (easy) way to pre-compile and save the module, but generates very fast code
        -   `pypy` is another JIT solution which is very actively maintained

Some Hardware Considerations
----------------------------

-   I/O will kill performance, avoid as much as you can
    -   7200 rpm is not that much if you need to read/write a million times
        -   expectation value of 1/14400 min latency every time you access the disc
        -   a million writes
        -   that's about an hour! Of just waiting!
    -   Regardless of how much you actually read/write. If you do it in one go, you'll get away with one wait.
    -   OS filesystem and hard disc caches alleviate this, but cannot completely hide the effect and
        -   for reads they are **almost completely powerless** to help you!
    -   SSD is much better than HDD but the effect is still there
    -   interleave I/O with other tasks if you can
    -   printing to standard output is also very slow, so avoid excessive printing
-   Interconnect Latency
    -   affects a NUMA machine like COSMOS as well as distributed memory machines (clusters)
-   Interconnect Bandwidth
    -   easier to measure, and deal with than latency
    -   at least an order of magnitude slower than memory, so avoid
-   Memory subsystem performance
    -   NUMA causes issues even on single socket these days
    -   CPU's memory controller always operates on a *page* of memory
        -   sizes vary between 4kB, 2MB, 1GB
    -   78.6 GB/s (Broadwell) vs 915.2 GF/s gives 95 F/double!!!
    -   latency is an even bigger bugbear and much harder to measure/control
    -   caches help overcome both
        -   but introduce a degree of unpredictability
    -   cache is multi-level, only last level can keep up with core; prefetching
    -   set-associative
        -   M addresses map to the same set
        -   2<sup>N</sup> -way set associative cache N of M (\>\>2<sup>N</sup>) addresses in cache
        -   cache collision happens when CPU needs to cache \>2<sup>N</sup> addresses mapping to the same set
        -   cache collisions explain many unexpected performance decreases, especially when one has a an array with a dimension equal to some power of two
        -   typical value of N \< 10
    -   see [this](https://en.wikipedia.org/wiki/CPU_cache) for good read on caches
-   other on-core issues that have to do with parallelism
    -   *false sharing* affects many unsuspecting OpenMP parallelisations
        -   TODO!!! Try to demonstrate with a small code
    -   page ownership can also surprise in a NUMA machine if owner is not where expected
        -   very hard to control and hardware dependent, but usually **last writer** to a page owns it
        -   but determining what belongs to which page is difficult (except for big malloc()ed arrays)
-   in-core
    -   how to load a cache line
    -   branch misprediction
        -   [here](http://stackoverflow.com/questions/11227809/why-is-processing-a-sorted-array-faster-than-an-unsorted-array) is an example
        -   function calls are effectively branch misses
    -   pipeline stall
    -   pipeline flush

First Shot at Optimising the Laplacian
--------------------------------------

-   Recall the triple for-loop in the Laplacian above? It was the hot spot.
-   We'll forget about the other bits for now (we could not optimise the FFTs anyway)

``` {.python}
  import numpy
  import scipy
  import scipy.fftpack 
  import cProfile
  import time as timemod
  import pstats
  import os

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
  results = RunSome([{"func":"Laplacian1", "flop":(SIZE-2)**3*17}]+RunList)
```

-   **Rule \#1**: never use a `for` loop to operate on a numpy array

Node level optimisation: Use the Cores: multi- and manycore architectures
-------------------------------------------------------------------------

-   Python has something called *Global Interpreter Lock* (GIL) which makes threads almost useless for compute intensive tasks in python without relatively complicated tricks
    -   careful use of numpy arrays can avoid this
-   "Standard" way to use the cores in C/C++ is OpenMP
    -   these have no GIL, of course
    -   in this context OpenMP does nothing but multithread the code: sometimes better to do that manually
        -   e.g. when you need to call an OpenMP-parallelised library
            -   this "nesting" of OpenMP is supported but does limit your options
    -   cython can do that in python, too and we'll soon see how

C+Python = Cython: an optimised RHS
-----------------------------------

-   First, let's do a very simple "loop invariant motion" optimisation:
-   note that `d[i]` are the same for each point, so no point in recalculating their squares every time
    -   on C/C++/Fortran the compiler will *in principle* do this for you but it often fails so best do it by hand anyway
-   also have to adjust the `LGF` variable
-   we also forget about the poorly performing `Laplacian`:
    -   the better optimised versions of the code will be so much faster than `Laplacian` that using `SIZE=100` becomes impossible
    -   but we do not want to wait for those 10 minutes or so it takes to compute `SIZE=400`
    -   we choose 400 because that's about the biggest we can fit in the memory of a single core on most HPDA hardware

``` {.python}
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
```

-   the trick with redefining `dx2` and writing `*dx2` instead of `/dx2` has to do with the hardware: division is much slower than multiplication!
-   well, that wasn't much, but about 1% without really doing anything is not a bad start (on top of that 100x earlier)
-   do not even try to do `SIZE=400` with the for-loops: your runtime will go through the roof, oceans will dry, Sun will become a red giant, and quite probably the Universe suffer a heat death before your code returns (an over 100x speedup would not be unexpected)
-   but even with numpy this leaves room for improvement:
    -   it is still python with all the overhead an interpreted language implies
    -   it uses a single core only
    -   N.B. numpy's and scipy's BLAS and LAPACK routines (numpy.linalg, scipy.linalg) and possibly some others will use an external library to do the maths: if this library uses many cores, you get the benefit for free
    -   the code as it stands also happens to be bound by the speed of the MEMORY, not the CPU
    -   we have no idea how well the caches are used (would need to profile using more sophisticated tools)
-   next, we'll write an improved version using *cython*
    -   N.B. only ipython and jupyter can run this: normal python cannot
    -   we will deal with plain python later
-   a look at the code
    -   everything from `%%cython` to the next empty line will be saved to a temporary file, turned into a C code using cython and then compiled into a python module which is then imported
    -   when cython runs, it does not see our current namespace (it is a separate process), so we need to import whatever we use
    -   there is also a special `cimport` command, which imports "into C code"
    -   the `@cython` lines are decorators defined in cython which affect how cython treats the following function: we want no bounds checking on our arrays and we want \(1/0\) to produce \(\infty\) instead of python's `ZeroDivisionError`
    -   this is more or less standard cython preamble
    -   notice also the type definitions in the function definition: **always** type **everything** in cython as if you do not, cython treats them as python objects with all the performance penalty that implies
-   we'll also introduce the right datatypes: the `double` we used above just happens to be the same as an element of the `numpy.ndarray` we passed Laplacian

``` {.python}
  %%bash
  cat ../codes/python/cyLaplacian1.pyx
```

``` {.python}
  import pyximport
  pyximport.install(setup_args={'include_dirs': numpy.get_include()})
  import sys
  sys.path = ["../codes/python"]+sys.path
  import cyLaplacian1
  RunList.append({"func":"cyLaplacian1.cyLaplacian1", "flop":(SIZE-2)**3*14+3})
  results = RunSome(RunList)
```

-   that was not an impressive result: the `double` we used above just happens to be the same as an element of the `numpy.ndarray` we passed Laplacian: perhaps that was the cause? Let us define them more correctly.

``` {.python}
  %%bash
  cat ../codes/python/cyLaplacian2.pyx
```

``` {.python}
  import cyLaplacian2
  RunList.append({"func":"cyLaplacian2.cyLaplacian2", "flop":(SIZE-2)**3*14+3})
  results = RunSome(RunList)
```

-   That was not an impressive result: unfortunately as much as numpy likes array-operations, cython dislikes them. They prevent cython from leaving python-land behind.
-   **EXERCISE** run the last cell, repeating a few times:
    -   do the relative speeds of the routines change?
    -   if so, why?
    -   if so, which one is actually the fastest and why?
-   next we go back to explicit loops

``` {.python}
  %%bash
  cat ../codes/python/cyLaplacian3.pyx
```

``` {.python}
  import cyLaplacian3
  RunList.append({"func":"cyLaplacian3.cyLaplacian3", "flop":(SIZE-2)**3*14+3})
  results = RunSome(RunList)
```

-   that's more like it, but can we do more? Without touching the code, not much, but we can see if the compiler can do better!
-   cython can be told to pass flags to the compiler as follows

``` {.python}
  %%bash
  diff -Naur ../codes/python/cyLaplacian3.pyxbld ../codes/python/cyLaplacian4.pyxbld
```

``` {.python}
  import cyLaplacian4
  RunList.append({"func":"cyLaplacian4.cyLaplacian3", "flop":(SIZE-2)**3*14+3})
  results = RunSome(RunList)
```

-   python's integers gracefully overflow, C integers wrap around: we get an even bigger speedup by telling cython to conform to the C style, not python: `@cython.wraparound(False)`

``` {.python}
  %%bash
  cat ../codes/python/cyLaplacian5.pyx
```

``` {.python}
  import cyLaplacian5
  RunList.append({"func":"cyLaplacian5.cyLaplacian5", "flop":(SIZE-2)**3*14+3})
  results = RunSome(RunList)
```

-   but that's just one core: let's bring on the clon... I mean others!

``` {.python}
  %%bash
  cat ../codes/python/cyLaplacian5.pyx
```

``` {.python}
  import cyLaplacian6
  SIZE=500
  RunList.append({"func":"cyLaplacian6.cyLaplacian6", "flop":(SIZE-2)**3*14+3})
  RunList = [{"func":x["func"], "flop":(SIZE-2)**3*14+3} for x in RunList[1:]]
  results = RunSome(RunList)
```

-   the timings on my laptop

|function|best time (s)|
|--------|-------------|
|Laplacian1|N/A|
|Laplacian2|N/A|
|Laplacian3|5.993|
|cyLaplacian1|5.880|
|cyLaplacian2|5.880|
|cyLaplacian3|0.639|
|cyLaplacian4|0.627|
|cyLaplacian5|0.529|
|cyLaplacian6|0.661|

-   note that my timing for `cyLaplacian6` includes thread creation overheads!
    -   and has a horrible variance: the slowest time is over 1.4 seconds, whereas the non-threaded ones stay under 0.8 s
    -   you will see different behaviour on cosmos or any other proper HPC hardware
-   try changing the `num_threads` argument and see how this scales (you have 12 cores)

### Unintended side-effect

-   Memory consumption drops by 50% between `cyLaplacian2` and `cyLaplacian3`

### Bits and pieces

-   the examples involving `.pyx` files could be ran interactively as follows but then we have no clean way of running them non-interactively

``` {.python}
  %load_ext Cython
```

-   the above needs to be in its own cell before this

``` {.python}
  %%cython --compile-args=-Ofast --compile-args=-march=ivybridge --compile-args=-fno-tree-loop-vectorize --compile-args=-fno-tree-slp-vectorize --compile-args=-fno-ipa-cp-clone --compile-args=-funsafe-math-optimizations --compile-args=-fopenmp --link-args=-fopenmp
  import cython,numpy,os
  from cython.parallel import prange, parallel
  cimport numpy
  DTYPE=numpy.float64
  ctypedef numpy.float64_t DTYPE_t
  #@cython.profile(True)
  #@cython.linetrace(True)
  @cython.boundscheck(False)
  @cython.cdivision(True)
  @cython.wraparound(False)
  def cyLaplacian7(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d, int N):
      cdef int xmax = data.shape[0]
      cdef int ymax = data.shape[1]
      cdef int zmax = data.shape[2]
      cdef int num_threads = N
      cdef double dx2 = 1./(d[0]*d[0])
      cdef double dy2 = 1./(d[1]*d[1])
      cdef double dz2 = 1./(d[2]*d[2])
      cdef int ii, jj, kk
      #with nogil, parallel(num_threads=num_threads):
      #    for ii in prange(1,xmax-1,schedule="runtime"):
      for ii in xrange(1,xmax-1):
          for jj in xrange(1,ymax-1):
              for kk in xrange(1,zmax-1):
                  lapl[ii,jj,kk] = (
                        (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])*dx2 +
                        (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])*dy2 +
                        (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])*dz2 + 
                        (data[ii-1,jj,kk]*data[ii,jj,kk] + data[ii-1,jj,kk]*data[ii+1,jj,kk] + data[ii+1,jj,kk]*data[ii,jj,kk] +
                         data[ii,jj-1,kk]*data[ii,jj,kk] + data[ii,jj-1,kk]*data[ii,jj+1,kk] + data[ii,jj+1,kk]*data[ii,jj,kk] +
                         data[ii,jj,kk-1]*data[ii,jj,kk] + data[ii,jj,kk-1]*data[ii,jj,kk+1] + data[ii,jj,kk]*data[ii,jj,kk+1] +
                         data[ii-1,jj,kk-1]*data[ii,jj,kk-1] + data[ii-1,jj,kk-1]*data[ii+1,jj,kk-1] + data[ii+1,jj,kk-1]*data[ii,jj,kk-1] +
                         data[ii,jj-1,kk-1]*data[ii,jj,kk-1] + data[ii,jj-1,kk-1]*data[ii,jj+1,kk-1] + data[ii,jj+1,kk-1]*data[ii,jj,kk-1] +
                         data[ii-1,jj,kk-1]*data[ii,jj,kk-1] + data[ii,jj,kk-1]*data[ii-1,jj,kk+1] + data[ii,jj,kk]*data[ii-1,jj,kk+1])*dx2*dy2*dz2)
      return
```

``` {.python}
  AnotherRunList=[{"func":"cyLaplacian7", "flop":(SIZE-2)**3*(14+6*5+6+3)+3}]
  RunSome(RunList[-1:]+AnotherRunList)
```

-   and finally a look at parallel efficiency

``` {.python}
  %matplotlib notebook
```

<span class="label">Thread-level Scaling of cyLaplacian6</span>
``` {#fig:cyLaplacian6_scaling .python}
  import matplotlib.pyplot as plt
  results=[]
  for threads in range(1,13):
      os.environ["OMP_NUM_THREADS"]=str(threads)
      results.append(RunSome(RunList[-1:]))
  timedata = [x[1]['cyLaplacian6.cyLaplacian6'] for x in results]
  threads = numpy.arange(1,len(timedata)+1)
  timedata[0]/(timedata*threads)
  plt.plot(threads, timedata[0]/(timedata*threads))
```

![](images/cyLaplacian6_scaling.png)

OpenMP/TBB
----------

Vector Unit and GPU: SIMD/MIMD
------------------------------

