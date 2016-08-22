#!/usr/bin/env python

import numpy
import mpi4py
from mpi4py import MPI
import petsc4py
from petsc4py import PETSc

def testme(maxgrad, topology):
    '''In fact, the per-rank maximum occurs in z-direction at *non-ghosted* lattice point
    (xmax-1, ymax-1,0) for ranks at the "left" side of non-periodic "0" (=Z!) dimension
    where xmax, ymax, zmax refer to the maximum values in the *non-ghosted* lattice
    (i.e. sizes-parameter given to the constructor of rankinfo), and counting starts from
    the [1,1,1] of the ghosted lattice (i.e. first interior point); for all other ranks,
    the maximum is in y-direction at (0,ymax-1,zmax-1). I.e. is sizes==[3,4,5] these are
    at [3,4,1] and [1,4,5] of the ghosted lattice

    The value at *non-ghosted* [x,y,z] == (z+zmax*(y+ymax*(x))+rank)**2, so for the whole
    ghosted lattice the value at [x+1,y+1,z+1] == (z+zmax*(y+ymax*(x))+rank)**2.

    Hence the expected per-rank maximum is for ranks at "left" boundary (recall the
    boundary condition is lattice[boundary]=0):

    max1 = (((0+1)+zmax*((ymax-1)+ymax*(xmax-1))+rank)**2-0)/2

    and the other ranks have (note that the y-direction is periodic, so ymax means 1):

    max2 = (((zmax-1)+zmax*((1)+ymax*(0))+rank)**2-((zmax-1)+zmax*((ymax-2)+ymax*(0))+rank)**2)/2

    '''
    size=topology.Get_size()
    rank=topology.Get_rank()
    expected=[1568,1600,1640,1680,1720,1760,1800,1840]
    return maxgrad == expected[size-1]
def initialise_values(dm, vec_l, vec_g):
    '''Local arrays need to be STENCIL*2 bigger than the "real world" in each dimension'''
    sw = dm.getStencilWidth()
    ranges=numpy.array(dm.getRanges())
    lens=(numpy.diff(ranges)).T[0]
    array_g=dm.getVecArray(vec_g)
    array_g[:,:,:] = ((numpy.arange(lens.prod())+dm.getComm().Get_rank())**2).reshape(lens)
    dm.globalToLocal(vec_g, vec_l)
    array_l=dm.getVecArray(vec_l)
    ranges = numpy.array(dm.getGhostRanges())
    lens=(numpy.diff(ranges)).T[0]
    (xs,xe),(ys,ye),(zs,ze) = ranges
    array_l[xs:xe,ys:ye,zs:ze] = numpy.zeros((lens).prod()).reshape(lens)
    return
def find_max_grad(dm, vec_l, vec_g):
    dm.globalToLocal(vec_g, vec_l)
    array=dm.getVecArray(vec_l)
    (xs,xm),(ys,ye),(zs,ze) = dm.getRanges()
    sw=dm.getStencilWidth()
    print xs+sw,xm+sw,ys+sw,ye+sw,zs+sw,ze+sw, array[:,:,:].shape
    gradients=numpy.array(numpy.gradient(array[:,:,:]))[:,xs+sw:xm+sw,ys+sw:ye+sw,zs+sw:ze+sw]
    print xs+sw,xm+sw,ys+sw,ye+sw,zs+sw,ze+sw, gradients[:,:,:,:].shape
    maxgrad_local = numpy.array(gradients).max()
    maxgrad_global = numpy.zeros_like(maxgrad_local)
    dm.getComm().tompi4py().Allreduce([maxgrad_local, MPI.DOUBLE],
                                      [maxgrad_global, MPI.DOUBLE],
                                      op=MPI.MAX)
    return maxgrad_local, maxgrad_global

def main():
    dims=tuple(MPI.Compute_dims(MPI.COMM_WORLD.Get_size(),3))
    dm = PETSc.DMDA().create(dim=len(dims), ownership_ranges=(numpy.array([3]), numpy.array([4]), numpy.array([5])),
                             proc_sizes=dims,
                             boundary_type=(PETSc.DMDA.BoundaryType.PERIODIC,
                                            PETSc.DMDA.BoundaryType.PERIODIC,
                                            PETSc.DMDA.BoundaryType.GHOSTED),
                             stencil_type=PETSc.DMDA.StencilType.BOX,
                             stencil_width = 1, dof = 1, comm = PETSc.COMM_WORLD, setup = True)
    vec_l=dm.createLocalVector()
    vec_g=dm.createGlobalVector()
    initialise_values(dm, vec_l, vec_g)
    result_l, result_g = find_max_grad(dm, vec_l, vec_g)
    PETSc.Sys.syncPrint("Rank {rank} had max gradient {maxgrad_l} while the global was {maxgrad_g}."
                     .format(
                         rank=dm.getComm().getRank(),
                         maxgrad_l=result_l,
                         maxgrad_g=result_g))
    if (dm.getComm().getRank() == 0):
        if (testme(result_g, dm.getComm())):
            print("Result is correct.")
        else:
            print("Result is incorrect!")

if (__name__ == "__main__"):
    main()
