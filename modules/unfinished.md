from practices
==============

Cookbook: TODO!!! what goes in here???
--------------------------------------

TODO Best Practices, part 1: basic libraries
--------------------------------------------

-   use them, no point in writing your own unless you're a researcher in algorithm implementation: others are paid to develop them for you
-   of course, it's useful to LEARN how algorithms work by writing your own, but…
-   BLAS for linear algebra manipulations
-   LAPACK for small linear equations
-   there are several options for large linear equations which are discussed later
    -   hopefully your matrix is mostly zeros so can use **sparse matrix** representations
-   Remember: never invert a matrix numerically
    -   slow
    -   non-restartable
    -   inaccurate
    -   typically unstable
    -   iterative solution of the equation wins on all counts
        -   even when you need all eigenvalues (=the inverse)
        -   due to controllable and better accuracy
    -   ok, you may invert a diagonal matrix if you really want
-   non-linear equations: always iteratively solve linear ones
-   bunch of other libraries for Fourier, F(x)=0, Runge-Kutta etc; more on them later

### Examples/cookbook

-   matrix "solve" using LAPACK (And no, Ben, no preconditioning yet)
-   oops, ran out of memory! What now?

TODO (Will move to good practices section!) Open Data Policies
--------------------------------------------------------------

[More here](http://www.data.cam.ac.uk/) but it is something you should probably be prepared for.

Cambridge FAQ on Open Data says:

> 1.  Do I need to share my source code?
>
> If your source code is necessary to validate your research findings, then you are expected to share it.

It is not clear to me how **your** source would **ever** be necessary to validate the results but best prepare for publishing nevertheless.

Which also relates to

### Copyright and Licencing and Publishing a Program

Crash Course on Other Libraries?
================================

-   BLAS
-   LAPACK
-   ScaLAPACK
-   SLEPc
-   FEniCS/dolfin (FEM)
-   ClawPACK/PyCLAW (FVM)
-   FFT
-   Trilinos
-   More Tools and Good Practices

Offload to an accelerator or GPU
--------------------------------

-   Provides much higher performance/watt than normal CPU
-   We use Xeon Phi in the examples; GPU is similar but slightly trickier
-   Can be done explicitly, but almost never worth the effort: Intel's compiler has two ways to offload using compiler directives (pragmas) only, LEO and OpenMP.
-   GPU very popular in e.g. machine learning and neural networks, so transferable skill

### Example/Cookbook

-   some basic example
-   courses available

Debugging
---------

-   Your code does not work or produces an incorrect result: you want a debugger
-   cosmos has Allinea's DDT, but any debugger will
    -   show you your variable's values at any position in the code (unless they are optimised away)
    -   be able to step one source-code line at a time
    -   insert breakpoints
    -   find where the crash occurred (may need you to enable core file output: \`ulimit -c unlimited\`
-   Further resources!

### Example Debugging

-   buffer overflow / array access out of bounds / write() to a NULL or closed file or …
-   Big Computers: Parallel Processing

High Performance Computer Architecture
--------------------------------------

### Terminology

-   core
-   process
-   thread
-   distributed processing
-   interprocess communication

### Memory layout

-   access patterns: striding, re-reading, …
-   access cost: CPU much faster than RAM
-   NUMA: not all memory is equal (OpenMP and KNL issues)

MPI
---

-   By far the most common way to handle very big problems
-   Either to access more memory than a single machine (**node**) has or solve a problem faster by bringing more machines to bear
-   Wastes some resources to interprocess communications: scaling
    -   weak scaling: access more memory
    -   strong scaling: solve quicker
    -   strong scaling will eventually fail
-   Break your problem into as independent chunks as possible
    -   completely independent: embarrassingly parallel (most parallel I/O)
    -   solving a PDE: each node processes a simple subset of the domain, but needs to communicate on the edges
    -   moving particles cause issues with load-balancing: genuinely hard to solve
        -   redistributing particles between nodes is very slow
        -   not redistributing is not acceptable either
        -   can do different things on different nodes but only suits certain situations
-   Explicit inter-node communication model: message passing
    -   as noted earlier, this communication comes with a cost in latency
    -   has relatively limited bandwidth
    -   must be minimised
    -   can lead to deadlocks, be careful! (example?)
-   Think parallel and distributed from the beginning: saves you from a lot of trouble later
-   Think scaling, too: very hard to change an algorithm which does not scale to one which does after the whole program is written around it
    -   any global algorithm suffers from poor scaling
    -   unfortunately this includes Fourier, so think hard whether you need it or not: for just solving an equation you probably don't (Fast Multipole Method, hybrid…)
-   Should rarely need directly: libraries like PETSc, SLEPc, Chombo, Trilinos
-   Pointers to courses (UIS?)

### Basic example/cookbook:

-   read in/initialise data
-   process data
-   output data
-   and same with PETSc
-   in python

OpenMP
------

-   compiler-based approach to parallel programming (and some other things, too)
-   can also be used to offload to accelerators/GPUs
-   needs a single, shared memory node to operate: use MPI to distribute across nodes, OpenMP to parallelise inside a node
-   cosmos has an unusual case of shared memory across nodes (properly called NUMA-nodes in this case), so both work
-   OpenMP and NUMA issues
-   OpenMP is shared memory model with implicit parallelism, so must be careful with what is shared and what is not
    -   false sharing
    -   data corruption can occur
    -   correct which is correct on one thread can suddenly be incorrect with OpenMP parallelism
    -   must use critical/atomic sections to guard shared written data
        -   effectively non-parallel region in an otherwise parallelised chunk
        -   example
-   OpenMP can also deadlock
-   we have course material, can even run a course if needed

### Basic example/cookbook

-   solve the same as with MPI

Hybrid MPI+OpenMP
-----------------

### Just an Example

Profiling, Visualisation, ...?
==============================

Profiling
---------

-   What is this and why should I?
-   VTune, MAP, HPCToolkit(, tau, PAPI)

### Example session?

Visualisation
-------------

-   matplotlib for 2D
-   paraview (stereo!!!) and visit for 3D
-   python scripting
-   xdmf files
-   OSPRay?

### Examples/Cookbook

-   at least read a hdf5 file using xdmf
-   isosurfaces
-   streamlines
-   volume rendering
-   Example Codes in a Cookbook / Exercises

Root Finding (\(F(x)=0\))
-------------------------

-   let N be the number of elements of x typically \(N>>10^6\), even billions
-   Newton scales as \(O(N^2)\): for dense problems now we DO need to think about memory
    -   consider a quasi-Newton method, preferably a LMVM like BFGS
    -   consider it even if memory does not constrain you as the Hessian inversion (even when done iteratively) is quite costly compared to a quasi-Newton method's approximation
-   quite often conjugate gradient is efficient enough
-   use a proper library again so swapping between algorithms is simply a matter of changing a command line parameter!
-   Elliptic PDE's fall into this category (both linear and non-linear should be treated iteratively)
-   how to find a global minimum? GA and MC?
-   secant may be better in 1D but in 1D you are not really doing HPC
-   non-differentiable problems (Carola)

### Example/cookbook

-   Solve ? with PETSc using several algorithms (but no Hessian?)

Integration
-----------

-   not sure what to say here

Inter- and extrapolation
------------------------

-   not sure of this either
-   spline is evil

Representing a PDE in numerical, discrete form
----------------------------------------------

-   Of course, these become \(F(x)=0\) once discretised
-   Finite Differences
    -   Pros: conceptually simple, easy to write
    -   Cons: hard to improve accuracy once written, values between points
-   Finite Elements
    -   Pros: can handle complicated geometries easily, mathematically very well understood
    -   Cons: needs a weak form of the PDE, gruelling hard to implement from scratch
-   Finite Volumes
-   Again, use libraries: FEniCS/dolfin for FEM, FVM?

### Example/cookbook

-   Poisson in all three
-   And in funny geometry using FEM

Time Evolution
--------------

-   Explicit Timestepping
    -   RK4
    -   Dormand-Prince
    -   low memory RK (check details)
    -   CFL
-   Implicit Timestepping
    -   backward Euler
    -   Crank-Nicholson
    -   Adams–Bashforth, Adams–Moulton
    -   the step-internal equation solving usually too costly but for stiff problems and problems with very restrictive CFL the price may be acceptable (see IMEX)
-   Stability (A-stability)
    -   Dahlquist Barrier
-   Implicit-Explicit etc

### Examples/Cookbook

-   PETSc provides a nice interface with command-line swappable algorithms
    -   you need to provide Jacobian for Implicit ones unless you want even slower code

Large Matrices
--------------

-   Avoid dense matrices if you can, but if you cannot, ScaLAPACK and EigenExa are your friends (PETSc can do dense, too, but probably not as efficiently)
-   For sparse matrices: PETSc, SLEPc
-   Even better than sparse: **shell matrix**
    -   need to know how to get element \(a_{ij}\) from \(i,j\)
    -   no need to store the matrix at all!
    -   PETSc has extensive support
    -   sometimes called "matrix free" methods, algorithms etc but that's confusing as some methods genuinely have no matrices so they don't have shell matrices either
-   Decompositions and eigenvalues
    -   GMRES (PETSc)
    -   Krylov-Schur (SLEPc)
    -   preconditioning

### Examples/Cookbook

-   Find (some) eigenvalues of dense, sparse, and shell

Spectral Methods
----------------

-   FFT from FFTW, MKL
-   very elegant, especially on pen and paper, but not on computer: avoid due to scalability issues

Random Numbers
--------------

-   PETSc has a parallel random number generator
-   if not using PETSc, SPRNG is a decent parallel one
-   of course the numbers are only as random as the seed or operating system entropy collector

### Examples/Cookbook

-   just a worked out example for both libraries
-   Science Topic 1
-   Science Topic 2
-   Science Topic 3
-   Science Topic 4
-   foobar
-   The petsc4py TS example achieves 3.5% of peak performance for the whole routine on an Ivy Bridge class cpu.
    -   the "computational kernel" is significantly better
        -   but since we are mostly interested in OpenMP's SIMD and offload capabilities, we'll cover them very quickly

### our RHS

