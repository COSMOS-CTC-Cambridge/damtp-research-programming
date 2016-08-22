#!/usr/bin/env python
# Test different params: -ts_exact_final_time stepover -ts_max_it 1000 -ts_max_steps -ts_final_time 1e3 -ts_type rk -ts_view -ts_monitor -ts_monitor_solution_vtk filename-%04D.vts  -da_grid_x 50 -da_grid_y 40 -da_grid_z 30

from __future__ import division
import sys
import time
import numpy
import mpi4py
from mpi4py import MPI
import petsc4py
petsc4py.init(sys.argv)
from petsc4py import PETSc


class convection_diffusion(object):
    '''
    Normally, convection-diffusion equation reads

    c\rho ( dT/dt + e u dT/dx) = \lambda d^2T/dx^2 + Q

    but we do not want dT/dx term to complicate matters, so we set e=0, effectively making
    our system completely solid with no liquid component. Furthermore, as Q is just a
    source term and hence can absorb any constants, we rescale to

    dT/dt = g d^2T/dt^2 + Q,

    which of course assumes c\rho \ne 0, but if it were zero, we'd have a stupid equation
    anyway.
    '''
    
    def __init__(self, dm, dx_i):
        self.dm = dm
        self.dx = dx_i["dx"]
        self.dy = dx_i["dy"]
        self.dz = dx_i["dz"]
        self.local_field = self.dm.createLocalVector()
        self.g = self.dm.createGlobalVector()
        self.Q = self.dm.createGlobalVector()
        self.dOh = self.dm.createGlobalVector()
        mx, my, mz = self.dm.getSizes()
        # for now, we just have a cuboid domain
        self.phys = {"minx": -self.dx*(mx+1)/2, "maxx": +self.dx*(mx+1)/2,
                     "miny": -self.dy*(my+1)/2, "maxy": +self.dy*(my+1)/2,
                     "minz": -self.dz*(mz+1)/2, "maxz": +self.dz*(mz+1)/2}
    
    @property
    def stencil_width(self):
        return self.dm.getStencilWidth()

    def create_initial_guess(self, field):
        ''''
        An alternative, simpler but more memory hungry, way to create an initial guess:
        this creates an extra copy of the whole lattice data!
        '''
        field_ = self.dm.getVecArray(field)
        g_ = self.dm.getVecArray(self.g)
        Q_ = self.dm.getVecArray(self.Q)
        field_[:] = numpy.random.random(field_.shape)
        # we demonstrate how to have a different g at each point, but we use a constant
        # here
        g_[:] = numpy.ones_like(field_)
        # Gaussian source at origin
        (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
        Xs = self.phys["minx"] + self.dx*(xs+1)
        Xm = Xs + self.dx*(xe-xs-1)
        Ys = self.phys["miny"] + self.dy*(ys+1)
        Ym = Ys + self.dy*(ye-ys-1)
        Zs = self.phys["minz"] + self.dz*(zs+1)
        Zm = Zs + self.dz*(ze-zs-1)
        X,Y,Z = numpy.mgrid[Xs:Xm:(xe-xs)*1j,
                            Ys:Ym:(ye-ys)*1j,
                            Zs:Zm:(ze-zs)*1j]
        Q_[:,:,:] = numpy.exp(-(X**2+Y**2+Z**2))
        # TODO!!! Why this only affects boundaries?
        lf = self.dm.getVecArray(self.local_field)
        lf[:,:,:]=0.1
        
    def monitor(self, snes, iter, fnorm):
        sol = snes.getSolution()
        field_array = self.dm.getVecArray(sol)
    
    def rhs(self, snes, ftime, field, rhs):
        '''
        This is rhs in the time-stepping sense, not PDE sense, i.e. everything by dT/dt.
        '''
        # we need a /ghosted/ work data, so get that and put into self.local_field
        self.dm.globalToLocal(field, self.local_field)
        # what is our ghosted LHS box like
        field_array = self.dm.getVecArray(self.local_field)
        # what is our RHS box like?
        # use nice N-dimensional indexing instead of linear (performance issue?)
        rhs_array = self.dm.getVecArray(rhs)
        # just in case, we zero rhs (optimise: remove this: does it still work? Reliably?)
        rhs_array[:]=0
        # we need self.g as an array, too
        g_ = self.dm.getVecArray(self.g)
        Q_ = self.dm.getVecArray(self.Q)
        # get our array index ranges; note that these are GLOBAL, so cannot use python's
        # usual indexing like [-1]; we could get these also by calling the method
        # self.dm.getGhostCorners() or self.dm.getCorners()
        (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
        dx,dy,dz=self.dx,self.dy,self.dz
        # compute the Laplacian
        lapl = (
            (field_array[xs-1:xe-1,ys:ye,zs:ze]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs+1:xe+1,ys:ye,zs:ze])/dx*dy*dz +
            (field_array[xs:xe,ys-1:ye-1,zs:ze]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs:xe,ys+1:ye+1,zs:ze])/dy*dx*dz +
            (field_array[xs:xe,ys:ye,zs-1:ze-1]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs:xe,ys:ye,zs+1:ze+1])/dz*dx*dy)
        # update the right hand side
        rhs_array[:] = (g_[:,:,:]*lapl[:,:,:] +
                        Q_[:,:,:]*dx*dy*dz)
        # flops from lapl/point:     6*3
        # flops from the rest/point: 5
        log.addFlops((6*3+5)*(xe-xs)*(ye-ys)*(ze-zs))
        return
    
    def formJacobian(self, snes, X, J, P):
        '''
        Notice that the Laplacian stencil touches lattice points (x varies fastest)
        x,y,z-1   => comp + NCOMP*(x   + Nx*(y   + Ny*z-1))
        x,y-1,z   => comp + NCOMP*(x   + Nx*(y-1 + Ny*z  ))
        x-1,y,z   => comp + NCOMP*(x-1 + Nx*(y   + Ny*z  ))
        x,y,z     => comp + NCOMP*(x   + Nx*(y   + Ny*z  ))
        x+1,y,z   => comp + NCOMP*(x+1 + Nx*(y   + Ny*z  ))
        x,y+1,z   => comp + NCOMP*(x   + Nx*(y+1 + Ny*z  ))
        x,y,z+1   => comp + NCOMP*(x   + Nx*(y   + Ny*z+1))
        and of course g touches lattice point x,y,z, so our Jacobian is non-zero only at
        these points! Can therefore use sparse matrix format or even a shell matrix!
        '''
        # two familiar calls
        self.dm.globalToLocal(X, self.local_field)
        field_array = self.dm.getVecArray(self.local_field)
        # we need self.g as an array, too
        g_ = self.dm.getVecArray(self.g)
        # this is not technically necessary if the non-zero structure does not change but
        # safer to set everything to zero anyway (can optimise later)
        P.zeroEntries()
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
                    u = field_array[i,j,k]
                    # we write 1+1+1 to identify the place where different lattice
                    # spacings should go TODO!!!
                    diag = -2.0*(dx*dy/dz+dx*dz/dy+dy*dz/dx) - g_[i,j,k]*2*field_array[i,j,k]*dx*dy*dz
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
                        P.setValueStencil(row, col, value)
        # work some magic to put the distributed matrix together
        P.assemble()
        if (J != P):
            J.assemble() # matrix-free operator
        # our non-zero pattern stays the same for all iterations, so we tell PETSc that
        # (it allows some optimisations inside PETSc)
        return PETSc.Mat.Structure.SAME_NONZERO_PATTERN

stype = PETSc.DMDA.StencilType.BOX
bx    = PETSc.DMDA.BoundaryType.GHOSTED
by    = PETSc.DMDA.BoundaryType.GHOSTED
bz    = PETSc.DMDA.BoundaryType.GHOSTED
comm = PETSc.COMM_WORLD
rank = comm.rank
OptDB = PETSc.Options() #get PETSc option DB
#M = OptDB.getInt('M', 11)
#N = OptDB.getInt('N', 7)
#P = OptDB.getInt('P', 5)
M,N,P = -11, -7, -5
m = OptDB.getInt('m', PETSc.DECIDE)
n = OptDB.getInt('n', PETSc.DECIDE)
p = OptDB.getInt('p', PETSc.DECIDE)
dm = PETSc.DMDA().create(dim=3, sizes = (M,N,P), proc_sizes=(m,n,p),
                         boundary_type=(bx,by,bz), stencil_type=stype,
                         stencil_width = 1, dof = 1, comm = comm, setup = False)
dm.setFromOptions()
dm.setUp()
convdiff_problem = convection_diffusion(dm, {"dx":0.1, "dy":0.1, "dz":0.1})

# prepare the initial conditions
rhs = dm.createGlobalVector()

# go do fun things with Poisson
# set up the SNES context
ts = PETSc.TS().create()
ts.setDM(dm)
ts.setRHSFunction(convdiff_problem.rhs, rhs)
ts.setDuration(100, 1.e10)

#--------------------------------------------------------------------------------
# finish the TS setup
#--------------------------------------------------------------------------------
# set any -ts commend-line options (including those we checked above)
ts.setFromOptions()

# create an initial guess
field = dm.createGlobalVector()
convdiff_problem.create_initial_guess(field)

# have fun (and measure how long fun takes)
log=PETSc.Log()
print("Flops logged: {flops}".format(flops=log.getFlops()))
import cProfile
start = time.clock()
cProfile.run("ts.solve(field)")
end = time.clock()
print("Flops logged: {flops}".format(flops=log.getFlops()))
# and plot
U = dm.createNaturalVector()
dm.globalToNatural(field, U)

# for debugging
lf_ = convdiff_problem.dm.getVecArray(convdiff_problem.local_field)
f_ = convdiff_problem.dm.getVecArray(field)
sol_ = convdiff_problem.dm.getVecArray(ts.getSolution())
rhs_ = convdiff_problem.dm.getVecArray(rhs)
# ouput some statistics
if (dm.getComm().getRank()==0):
    timespent=(end-start)
    # the log is per-rank
    flop=log.getFlops()/1e9
    print("TS Function evaluations: {iter}; time spent solving: {time} s at {flops} GFLOP/s = {ppp}% peak on 2.5 GHz Ivy Bridge".format(
        iter=ts.getStepNumber(),
        flops=flop/timespent,
        ppp = flop/(2.5*timespent*8)*100,
        time=timespent)
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

