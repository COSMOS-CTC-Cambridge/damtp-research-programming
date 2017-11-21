#!/usr/bin/env python3
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

bx    = PETSc.DMDA.BoundaryType.PERIODIC
by    = PETSc.DMDA.BoundaryType.PERIODIC
bz    = PETSc.DMDA.BoundaryType.PERIODIC

comm = PETSc.COMM_WORLD

OptDB = PETSc.Options() #get PETSc option DB
m = OptDB.getInt('m', PETSc.DECIDE)
n = OptDB.getInt('n', PETSc.DECIDE)
p = OptDB.getInt('p', PETSc.DECIDE)

dm = PETSc.DMDA().create(dim=3, sizes = (-6,-8,-5), proc_sizes=(m,n,p),
                         boundary_type=(bx,by,bz), stencil_type=stype,
                         stencil_width = ssize, dof = 1, comm = comm, 
                         setup = False)
dm.setFromOptions()
dm.setUp()

data = dm.createGlobalVector()

def initialise(dm, field):
    field_ = dm.getVecArray(field)
    (zs, ze), (ys, ye), (xs, xe) = dm.getRanges()
    sizes = dm.getSizes()
    for z in range(zs,ze):
        for y in range(ys,ye):
            start = (xs + (y)*sizes[2] +
                     (z)*sizes[1]*sizes[2])
            stop = start + (xe-xs)
            field_[z,y,:] = numpy.arange(start, stop, step=1)**2
    return

def compute_grad(dm, field, dmgrad, grad):
    local_field = dm.createLocalVector()
    dm.globalToLocal(field, local_field)
    field_array = dm.getVecArray(local_field)
    grad_array = dmgrad.getVecArray(grad)
    temp=numpy.array(numpy.gradient(field_array[:]))[:,1:-1,1:-1,1:-1]
    for coo in [0,1,2]:
        grad_array[:,:,:,coo] = temp[coo][:,:,:]

dmgrad = PETSc.DMDA().create(dim=3, sizes = dm.sizes,
                             proc_sizes=dm.proc_sizes,
                             boundary_type=(bx,by,bz), stencil_type=stype,
                             stencil_width = ssize, dof = 3, comm = comm,
                             setup = False)
dmgrad.setFromOptions()
dmgrad.setUp()
grads = dmgrad.createGlobalVector()

initialise(dm, data)
compute_grad(dm, data, dmgrad, grads)
maxgrad=grads.max()
if PETSc.COMM_WORLD.rank == 0:
    print("Global maximum of the gradient was {maxgrad}.".format(
        maxgrad=maxgrad))
    print("The result is {}.".format(["incorrect", "correct"][maxgrad[1] == 2*dm.sizes[2]*dm.sizes[1]*(-1+dm.sizes[2]*dm.sizes[1]*(dm.sizes[0]-1))]))
