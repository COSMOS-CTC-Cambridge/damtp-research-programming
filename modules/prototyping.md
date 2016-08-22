Prototyping Parallel Programs Using Python
==========================================

Linear Example: \(\nabla^2 \phi(x,y) = g(x,y)\)
-----------------------------------------------

### Direct Solve (\(O((Nx*Ny)^2)\))

Let's see what it looks like. First we need to import some modules; if you come from C/Fortran and are new to python, think of these as "use module" or "\#include \<module.h\>" lines combined with "-lmodule"

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
  import cProfile
```

Next we need to set up some infrastructure. `PETSc.DMDA` is the most basic distributed data manager and its `StencilType` and `BoundaryType` attributes just define what shape region around a grid point is needed to compute whatever we want to compute at that point (options are `BOX` and `STAR`); `ssize` will become the size of this stencil later.

``` {.python}
  stype = PETSc.DMDA.StencilType.BOX
  ssize = 1
```

Boundaries of the lattice can be `NONE`, `GHOSTED`, or `PERIODIC`; `GHOSTED` means the ghost points exist on the external boundary, too. Those can be used to store boundary conditions. With `NONE` you need to special case the exterior boundary.

``` {.python}
  bx    = PETSc.DMDA.BoundaryType.GHOSTED
  by    = PETSc.DMDA.BoundaryType.GHOSTED
  bz    = PETSc.DMDA.BoundaryType.GHOSTED
```

We will have a look at MPI later, but with PETSc you rarely need any explicit MPI. For these examples, this is the only thing you need: the "name" of the MPI world we want to work in. For PETSc the top-level code almost invariably uses `PETSc.COMM_WORLD`.

``` {.python}
  comm = PETSc.COMM_WORLD
```

PETSc handles those pesky things called command line parameters (and configuration files!) for us, too. Let's see if we have been passed `m`, `n`, or `p`.

``` {.python}
  OptDB = PETSc.Options() #get PETSc option DB
  m = OptDB.getInt('m', PETSc.DECIDE)
  n = OptDB.getInt('n', PETSc.DECIDE)
  p = OptDB.getInt('p', PETSc.DECIDE)
```

This creates the distributed manager. Note how our variables above get used. There's one we did not explain: `dof` is simply the number of degrees of freedom (number of unknowns) per lattice site. The negative `sizes` values tells PETSc to get the value from command line parameters `-da_grid_x M`, `-da_grid_y N`, and `-da_grid_z P`, or use the magnitudes of the supplied parameter `sizes` if the corresponding cmdline one cannot be found. The latter two method calls handle the command line bit.

``` {.python}
  dm = PETSc.DMDA().create(dim=3, sizes = (-11,-7,-5), proc_sizes=(m,n,p),
                           boundary_type=(bx,by,bz), stencil_type=stype,
                           stencil_width = ssize, dof = 1, comm = comm, setup = False)
  dm.setFromOptions()
  dm.setUp()
```

At this stage we need to define our physics. We use the Poisson equation here, but any linear boundary value PDE would work. Obviously, initial value problems must be dealt differently. Comments on the code

`__init__()`  
-   called when class is instantiated; it just saves given lattice spacings `dx`, `dy`, `dz`; and creates a data structure `self.g` for the RHS.

`rhs()`  
-   the call to `self.dm.getVecArray()` is PETSc's most useful call: the returned data structure is a numpy array, indexable in almost the normal fashion with distributed-global indices
    -   almost: index `array[-1]` is not last element, but "left of 0": the first ghost element to the "left of 0"
-   we specify the value of `self.g` here simply as all ones, could be anything (as long as linear);
-   the `rhs_array` will gets its values in the usual fashion from 7-point Laplacian stencil
-   `self.dm.getRanges()` returns the distributed-local ranges of the lattice coordinates currect rank has
-   `self.dm.getSizes()` gives the distributed-global sizes of the lattice: needed in the loop for detecting when to apply boundary conditions
-   finally, a very inefficient loop setting the values: for most lattice points it is a `rhs_array[i,j,k] ` rhs<sub>array</sub>[i,j,k]= but this is only ran once, so not too important
-   the non-trivial values are the boundary conditions (i.e. u=7), see plot

![How a 2D slice at k=1 of the 3D data maps boundary conditions onto a 1D RHS vector; note that lattice points (i,j,k)=(1,1,0) and (1,1,2) also map to rhs(0) from outside the diagram.](file:images/boundary_conditions.png)

`compute_operators()`  
-   dealing with distributed matrices almost always starts with `A.zeroEntries()` and ends with `A.assemble()`
-   `PETSc.Mat.Stencil()` returns a convenient helper object to deal with setting sparse matrix values simply by using the lattice coordinates instead of tranaforming them to matrix indices
    -   slight performance penalty but again we do this just once
-   `row.index` and `col.index` are used to calculate the matrix indices from lattice indices; `row.field` and `col.field` refer to which degree of freedom these values apply to in said conversion (the `dof` in the `PETSc.DMDA().create()`)
-   finally, `A.setValueStencil()` puts the values in

``` {.python}
  class poisson(object):
      def __init__(self, dm, dx_i):
          self.dm = dm
          self.dx = dx_i["dx"]
          self.dy = dx_i["dy"]
          self.dz = dx_i["dz"]
          self.g = self.dm.createGlobalVector()

      def rhs(self, ksp, rhs):
          dx,dy,dz=self.dx,self.dy,self.dz
          rhs_array = self.dm.getVecArray(rhs)
          g_ = self.dm.getVecArray(self.g)
          g_[:] = 1.0 
          rhs_array[:]=g_[:]*numpy.ones_like(rhs_array)*dx*dy*dz
          (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
          mx,my,mz = self.dm.getSizes()
          for k in range(zs, ze):
              for j in range(ys, ye):
                  for i in range(xs, xe):
                          rhs_array[i,j,k] = (rhs_array[i,j,k] +
                                              7.0*(((k==0) + (k==mz-1))*dx*dy/dz +
                                                   ((j==0) + (j==my-1))*dx*dz/dy +
                                                   ((i==0) + (i==mx-1))*dy*dz/dx))
          return

      def compute_operators(self, ksp, J, A):
          A.zeroEntries()
          row = PETSc.Mat.Stencil()
          col = PETSc.Mat.Stencil()
          (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
          dx,dy,dz=self.dx,self.dy,self.dz
          for k in range(zs, ze):
              for j in range(ys, ye):
                  for i in range(xs, xe):
                      row.index = (i,j,k)
                      row.field = 0
                      diag = -2.0*(dx*dy/dz+dx*dz/dy+dy*dz/dx)
                      for index, value in [
                              ((i,j,k-1), +1.0/dz*dx*dy),
                              ((i,j-1,k), +1.0/dy*dx*dz),
                              ((i-1,j,k), +1.0/dx*dy*dz),
                              ((i, j, k), diag),
                              ((i+1,j,k), +1.0/dx*dy*dz),
                              ((i,j+1,k), +1.0/dy*dx*dz),
                              ((i,j,k+1), +1.0/dz*dx*dy)]:
                          col.index = index
                          col.field = 0
                          A.setValueStencil(row, col, value)
          A.assemble()
          return None
  poisson_problem = poisson(dm, {"dx":0.1, "dy":0.1, "dz":0.1})
```

Now we are ready to set up the solver. First we create a KSP solver,

``` {.python}
  ksp = PETSc.KSP().create()
```

tell it that we are working with a distributed manager (`ksp.setDM()`),

``` {.python}
  ksp.setDM(dm)
```

then tell the solver how to generate the RHS and matrix

``` {.python}
  ksp.setComputeRHS(poisson_problem.rhs)
  ksp.setComputeOperators(poisson_problem.compute_operators)
```

and finally finish the setup by accommodating all configuration file and command-line options

``` {.python}
  ksp.setFromOptions()
```

Before we can solve the problem we need a workspace (`sol`) and an initial guess (`field`), which we just leave uninitialised now: for a KSP solver, that of course affects convergence speed but unlike Newton algorithms, it makes no difference otherwise: the inverse of the matrix is unique when it exists.

``` {.python}
  field = dm.createGlobalVector()
  sol = field.duplicate()
```

The solver would now normally be invoked with `ksp.solve(field,sol)` but we wrap this in python's built-in profiler to get some information of the efficiency of the code and where is spends its time: `time.clock()` just gives the CPU time used since either the beginning of the process and `cProfile.run()` sets up profiling and then gives its parameter to `exec` and outputs statistics after that finishes (i.e. in this case after divergence or convergence).

``` {.python}
  start = time.clock()
  cProfile.run("ksp.solve(field,sol)")
  end = time.clock()
```

Now we can have a look at the solution; we will later see how we could visualise this. The code in the git repo has a rudimentary visualiser built in.

``` {.python}
  ksp.getSolution()[:]
```

That program was actually ran in an MPI distributed parallel fashion, PETSc just hides almost all of it. The only hints of MPI are in the *LocalVector* and *COMM<sub>WORLD</sub>* names. In this case, it ran with just one processor core, for reasons of interactive python. We can run a proper 8-way-parallel (8 *ranks*) quite easily, though: all we need is a "magic" string `%%bash` in our code below. First `git` checks out the correct version of the training codebase and then mpirun executes the code with 8 ranks. Finally it reverts back to master branch.

``` {.bash}
  %%bash
  mpirun -np 8 python -- ../codes/python/poisson_ksp.py -da_grid_x 80 -da_grid_y 70 -da_grid_z 60
```

-   PETSc's "direct" Krylov SPace (KSP) solvers are iterative
    -   this avoids matrix inversion, which is and \(O(N^2.8)\) operation (Strassen; Coppersmith-Winograd is \(O(N^2.373)\) but not know to been ever implemented)
    -   iterative KSP solvers get away with iterating matrix-vector only, which is \(O(N^2)\)
    -   one thus hopes KSP solver does not take too many iterations compared to iterative inversion
-   Next we forget about linearity and use non-linear solvers to solve \(\nabla^2 \phi(x,y) - g(x,y) = 0\)

Non-linear Example: TODO!!! global vortex?
------------------------------------------

-   Use SNES, TS, TAU?

### Problems (which we'll fix later)

-   RHS is not very fast
-   Not very memory friendly (can you spot extra copies?)
-   Did we save it?
-   Did we look at it?
-   Jacobian!

Cookbook: TODO!!!
