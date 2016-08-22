#!/usr/bin/env python
'''
Try:
ID ME

'''

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


class poisson(object):
    def __init__(self, dm, dx_i):
        self.dm = dm
        self.dx = dx_i["dx"]
        self.dy = dx_i["dy"]
        self.dz = dx_i["dz"]
        self.g = self.dm.createGlobalVector()
    
    def rhs(self, ksp, rhs):
        '''
        Write Poisson equation as

        \nabla^2 f = g,

        and set the "rhs" to g(x,y,z) here, but pay attention to boundary conditions, too!
        '''
        # shortcuts
        dx,dy,dz=self.dx,self.dy,self.dz
        # use nice N-dimensional indexing instead of linear (performance issue?)
        rhs_array = self.dm.getVecArray(rhs)
        g_ = self.dm.getVecArray(self.g)
        g_[:] = 1.0 
        # just in case, we zero rhs (optimise: remove this: does it still work? Reliably?)
        # there is a simpler routine to set a Vec to all ones (or zeros) but this works more generally
        rhs_array[:]=g_[:]*numpy.ones_like(rhs_array)*dx*dy*dz
        # TODO!!! Boundary conditions!
        # this is familiar, too
        (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
        # shortcuts
        mx,my,mz = self.dm.getSizes()
        # this is a sparse matrix, so cannot use simple [indexes]
        for k in range(zs, ze):
            for j in range(ys, ye):
                for i in range(xs, xe):
                        rhs_array[i,j,k] = (rhs_array[i,j,k] +
                                            7.0*(((k==0) + (k==mz-1))*dx*dy/dz +
                                                 ((j==0) + (j==my-1))*dx*dz/dy +
                                                 ((i==0) + (i==mx-1))*dy*dz/dx))
        return
    
    def compute_operators(self, ksp, J, A):
        '''
        Notice that the operator stencil touches lattice points (x varies fastest)
        x,y,z-1   => comp + NCOMP*(x   + Nx*(y   + Ny*z-1))
        x,y-1,z   => comp + NCOMP*(x   + Nx*(y-1 + Ny*z  ))
        x-1,y,z   => comp + NCOMP*(x-1 + Nx*(y   + Ny*z  ))
        x,y,z     => comp + NCOMP*(x   + Nx*(y   + Ny*z  ))
        x+1,y,z   => comp + NCOMP*(x+1 + Nx*(y   + Ny*z  ))
        x,y+1,z   => comp + NCOMP*(x   + Nx*(y+1 + Ny*z  ))
        x,y,z+1   => comp + NCOMP*(x   + Nx*(y   + Ny*z+1))
        and of course g touches lattice point x,y,z, so our matrix is non-zero only at
        these points! Can therefore use sparse matrix format or even a shell matrix!

        Note also how we handle our boundary conditions: conventionally, boundary
        conditions are implicit, i.e. not solved for at all, but that requires fiddly
        matrix-filling routine, so we will rather just spend a bit extra time solving a
        few equations of the form f[0,0] == b.c., which if course should not slow us down
        really much at all.

        You can try the alternative and see how big the difference is!
        '''
        # this is not technically necessary if the non-zero structure does not change but
        # safer to set everything to zero anyway (can optimise later)
        A.zeroEntries()
        # TODO!!!
        row = PETSc.Mat.Stencil()
        col = PETSc.Mat.Stencil()
        # this is familiar, too
        (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
        # shortcuts
        dx,dy,dz=self.dx,self.dy,self.dz
        # this is a sparse matrix, so cannot use simple [indexes]
        for k in range(zs, ze):
            for j in range(ys, ye):
                for i in range(xs, xe):
                    row.index = (i,j,k)
                    row.field = 0
                    # diagonal term is "easy"
                    diag = -2.0*(dx*dy/dz+dx*dz/dy+dy*dz/dx)
                    # loop over the indices of ALL non-zero entries on this row and the
                    # values of the corresponding elements
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
                        # set the values in the sparse matrix
                        A.setValueStencil(row, col, value)
        # work some magic to put the distributed matrix together
        A.assemble()
        return None

stype = PETSc.DMDA.StencilType.BOX
ssize = 1
bx    = PETSc.DMDA.BoundaryType.GHOSTED
by    = PETSc.DMDA.BoundaryType.GHOSTED
bz    = PETSc.DMDA.BoundaryType.GHOSTED
comm = PETSc.COMM_WORLD
OptDB = PETSc.Options() #get PETSc option DB
m = OptDB.getInt('m', PETSc.DECIDE)
n = OptDB.getInt('n', PETSc.DECIDE)
p = OptDB.getInt('p', PETSc.DECIDE)
dm = PETSc.DMDA().create(dim=3, sizes = (-11,-7,-5), proc_sizes=(m,n,p),
                         boundary_type=(bx,by,bz), stencil_type=stype,
                         stencil_width = ssize, dof = 1, comm = comm, setup = False)
dm.setFromOptions()
dm.setUp()
# steady state poisson (or NLS?) equation...
# prepare the g(x,y) term
poisson_problem = poisson(dm, {"dx":0.1, "dy":0.1, "dz":0.1})

# go do fun things with Poisson
# set up the KSP context
ksp = PETSc.KSP().create()
ksp.setDM(dm)
# tell KSP where how to compute the RHS
# Note that for a non-multigrid code this could be replaced by a direct setup but as this
# will then be called just once, there's no point
ksp.setComputeRHS(poisson_problem.rhs)
# tell KSP how to create the matrix, too
ksp.setComputeOperators(poisson_problem.compute_operators)

#--------------------------------------------------------------------------------
# finish the KSP setup
#--------------------------------------------------------------------------------
# set any -ksp commend-line options (including those we checked above)
ksp.setFromOptions()

# create an initial guess
field = dm.createGlobalVector()
sol = field.duplicate()

# have fun (and measure how long fun takes)
cp=cProfile.Profile()
start = time.clock()
cp.runcall(ksp.solve, field, sol)
end = time.clock()
if (dm.getComm().getRank() == 0):
    print("Rank {rank} had the following profile.\nFor domain decomposed codes like this, the profiles will all be equivalent, up to variance.".format(rank=dm.getComm().getRank()))
    cp.print_stats()
# and plot
U = dm.createNaturalVector()
dm.globalToNatural(ksp.getSolution(), U)

# for debugging
f_ = poisson_problem.dm.getVecArray(field)
sol_ = poisson_problem.dm.getVecArray(ksp.getSolution())
#rhs_ = poisson_problem.dm.getVecArray(rhs)
# ouput some statistics
if (dm.getComm().getRank()==0):
    print("KSP iterations: {iter} and final norm: {norm}; time spent solving: {time} s".format(
        iter=ksp.getIterationNumber(),
        norm=ksp.getResidualNorm(),
        time=(end-start))
    )

if OptDB.getBool('plot_mpl', False):

    def plot_mpl(da, U):
        comm = da.getComm()
        rank = comm.getRank()
        scatter, U0 = PETSc.Scatter.toZero(U)
        scatter.scatter(U, U0, False, PETSc.Scatter.Mode.FORWARD)
        if rank == 0:
            try:
                from matplotlib import pylab
            except ImportError:
                PETSc.Sys.Print("matplotlib not available")
            else:
                from numpy import mgrid
                nx, ny, nz = da.sizes
                solution = U0[...].reshape(da.sizes,order="f")
                print da.sizes, da.getRanges()
                #xx, yy =  mgrid[0:1:1j*nx,0:1:1j*ny]
                pylab.contourf(solution[:, :,nz//2])
                #pylab.axis('equal')
                pylab.xlabel('X')
                pylab.ylabel('Y')
                pylab.title('Z/2')
                pylab.colorbar()
                pylab.show()
        comm.barrier()

    plot_mpl(dm, U)

