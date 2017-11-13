#!/usr/bin/env python
'''
Test different run-times: for params in "" "-snes_mf 1" "-snes_fd 1" "-snes_mf_operator 1" "-snes_fd_color 1" "-snes_fd 0 -snes_mf 0 -snes_fd_color 0 -snes_mf_operator 0"; do echo Params: $params; ipython  --pdb  --gui=wx -- nl_poisson_snes.py -snes_converged_reason -snes_monitor -da_grid_x 30 -da_grid_y 20 -da_grid_z 10  $params;done
 And also -snes_check_jacobian to check Jacobian

Try:

1. Direct Linear Solve With Actual Matrix
2. SNES with and without Jacobian AND
   1. no option (or all False) to get hand-written Jacobian
   2. Shell Jacobian -snes_mf
   3. Shell Jacobian Operator with -snes_mf_operator
   4. FD Jacobian -snes_fd
   5. Coloured FD Jacobian -snes_fs_color
3. TS
4. TAO

Total 1+2*4+1+1 = 11 cases.

- Using -snes_mf will cause no preconditioner to be used
- Giving no matrix-related options does not require Jacobian, but will use ILU preconditioner
- Explicitly calling Jacobian setup routines ...

Write nl Poisson equation as

        \nabla^2 f - g f^2 = 0,

and discretise using 2nd order 7-point central difference 3D Laplacian to get

        f(x+1,y,z) + f(x,y+1,z) + f(x,y,z+1) + f(x-1,y,z) + f(x,y-1,z) + f(x,y,z-1) - 6 f(x,y,z) - g(x,y,z)*f(x,y,z)**2 = 0

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

class nl_poisson(object):
    def __init__(self, dm, dx_i):
        self.dm = dm
        self.dx = dx_i["dx"]
        self.dy = dx_i["dy"]
        self.dz = dx_i["dz"]
        self.local_field = self.dm.createLocalVector()
        self.g = self.dm.createGlobalVector()
    @property
    def stencil_width(self):
        return self.dm.getStencilWidth()
    def create_initial_guess(self, field):
        field_ = self.dm.getVecArray(field)
        g_ = self.dm.getVecArray(self.g)
        field_[:] = numpy.random.random(field_.shape)
        g_[:] = numpy.ones_like(field_)
        lf = self.dm.getVecArray(self.local_field)
        lf[:,:,:]=-7.0
    def monitor(self, snes, iter, fnorm):
        sol = snes.getSolution()
        field_array = self.dm.getVecArray(sol)
    def rhs(self, snes, field, rhs):
        self.dm.globalToLocal(field, self.local_field)
        field_array = self.dm.getVecArray(self.local_field)
        rhs_array = self.dm.getVecArray(rhs)
        rhs_array[:]=0
        g_ = self.dm.getVecArray(self.g)
        (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
        dx,dy,dz=self.dx,self.dy,self.dz
        lapl = (
            (field_array[xs-1:xe-1,ys:ye,zs:ze]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs+1:xe+1,ys:ye,zs:ze])/dx*dy*dz +
            (field_array[xs:xe,ys-1:ye-1,zs:ze]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs:xe,ys+1:ye+1,zs:ze])/dy*dx*dz +
            (field_array[xs:xe,ys:ye,zs-1:ze-1]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs:xe,ys:ye,zs+1:ze+1])/dz*dx*dy)
        rhs_array[:] = (lapl[:,:,:] -
                        g_[:,:,:]*(field_array[xs:xe,ys:ye,zs:ze])**2*dx*dy*dz)
        return
    def formJacobian(self, snes, X, J, P):
        self.dm.globalToLocal(X, self.local_field)
        field_array = self.dm.getVecArray(self.local_field)
        g_ = self.dm.getVecArray(self.g)
        P.zeroEntries()
        row = PETSc.Mat.Stencil()
        col = PETSc.Mat.Stencil()
        (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
        dx,dy,dz=self.dx,self.dy,self.dz
        for k in range(zs, ze):
            for j in range(ys, ye):
                for i in range(xs, xe):
                    row.index = (i,j,k)
                    row.field = 0
                    u = field_array[i,j,k]
                    diag = (-2.0*(dx*dy/dz+dx*dz/dy+dy*dz/dx)
                            -g_[i,j,k]*2*field_array[i,j,k]*dx*dy*dz)
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
                        P.setValueStencil(row, col, value)
        P.assemble()
        if (J != P):
            J.assemble()
        return PETSc.Mat.Structure.SAME_NONZERO_PATTERN

stype = PETSc.DMDA.StencilType.BOX
bx    = PETSc.DMDA.BoundaryType.GHOSTED
by    = PETSc.DMDA.BoundaryType.GHOSTED
bz    = PETSc.DMDA.BoundaryType.GHOSTED
comm = PETSc.COMM_WORLD
rank = comm.rank
OptDB = PETSc.Options()
M,N,P = -11, -7, -5
m = OptDB.getInt('m', PETSc.DECIDE)
n = OptDB.getInt('n', PETSc.DECIDE)
p = OptDB.getInt('p', PETSc.DECIDE)
dm = PETSc.DMDA().create(dim=3, sizes = (M,N,P), proc_sizes=(m,n,p),
                         boundary_type=(bx,by,bz), stencil_type=stype,
                         stencil_width = 1, dof = 1, comm = comm,
                         setup = False)
dm.setFromOptions()
dm.setUp()
nl_poisson_problem = nl_poisson(dm, {"dx":0.1, "dy":0.1, "dz":0.1})
rhs = dm.createGlobalVector()
snes = PETSc.SNES().create()
snes.setDM(dm)
snes.setFunction(nl_poisson_problem.rhs, rhs)
snes.setMonitor(nl_poisson_problem.monitor)
if (OptDB.hasName("snes_mf")):
    mf=OptDB.getBool("snes_mf")
else:
    mf=None
if (OptDB.hasName("snes_fd")):
    fd=OptDB.getBool("snes_fd")
else:
    fd=None
if (OptDB.hasName("snes_mf_operator")):
    mfop=OptDB.getBool("snes_mf_operator")
else:
    mfop=None
if (OptDB.hasName("snes_fd_color")):
    fdcol=OptDB.getBool("snes_fd_color")
else:
    fdcol=None
print("Using FD={fd}, MF={mf}, FD Color={fdcol}, MF Operator={mfop}".format(
    fd=fd, mf=mf, fdcol=fdcol, mfop=mfop))
if not((mf) or (mfop) or (fd) or (fdcol)):
    print("Using hand-written Jacobian with a preconditioner"+
          "{prec}.".format(prec=snes.getKSP().getPC().getType()))
    J = dm.createMatrix()
    snes.setJacobian(nl_poisson_problem.formJacobian, J)
elif (mf or mfop):
    if (fd or fdcol):
        raise ValueError("Cannot have both MF and FD at the same time.")
elif (fd or fdcol or (fdcol==None)):
    if (mf or mfop):
        raise ValueError("Cannot have both FD and MF at the same time.")

snes.getKSP().setType("cg")
snes.setFromOptions()
field = dm.createGlobalVector()
nl_poisson_problem.create_initial_guess(field)

import cProfile
start = time.clock()
cProfile.run("snes.solve(None, field)")
end = time.clock()
