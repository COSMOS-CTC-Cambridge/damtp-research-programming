
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

vwr=PETSc.Viewer().createHDF5(fn.name, mode=PETSc.Viewer.Mode.WRITE)
vec1.view(vwr)
vwr.destroy()

vwr=PETSc.Viewer().createHDF5(fn.name, mode=PETSc.Viewer.Mode.READ)
vec2.load(vwr)
print("Are they equal? " + str(bool(vec1.equal(vec2))))
