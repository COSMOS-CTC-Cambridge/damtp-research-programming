#!/usr/bin/env python

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

ksp = PETSc.KSP().create()

ksp.setDM(dm)

ksp.setComputeRHS(poisson_problem.rhs)
ksp.setComputeOperators(poisson_problem.compute_operators)

ksp.setFromOptions()

field = dm.createGlobalVector()
sol = field.duplicate()

start = time.clock()
cProfile.run("ksp.solve(field,sol)", sort="time")
end = time.clock()

ksp.getSolution()[:]
