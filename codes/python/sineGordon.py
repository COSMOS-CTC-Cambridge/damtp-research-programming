#!/usr/bin/env python
# Test different run-times: for params in "" "-snes_mf 1" "-snes_fd 1" "-snes_mf_operator 1" "-snes_fd_color 1" "-snes_fd 0 -snes_mf 0 -snes_fd_color 0 -snes_mf_operator 0"; do echo Params: $params; ipython  --pdb  --gui=wx -- heat.py -snes_converged_reason -snes_monitor -da_grid_x 30 -da_grid_y 20 -da_grid_z 10  $params;done
# And also -snes_check_jacobian to check Jacobian
'''
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


class sineGordon(object):
    '''
    The static part of the sine-Gordon equation but in 3D:

    \nabla^2 \phi = m^2 \sin\phi


    and discretise using 2nd order 7-point central difference 3D Laplacian to get
    
    f(x+1,y,z) + f(x,y+1,z) + f(x,y,z+1) + f(x-1,y,z) + f(x,y-1,z) + f(x,y,z-1) - 6 f(x,y,z) - g(x,y,z) = 0

    '''
    
    def __init__(self, dm, dx_i, mass):
        self.dm = dm
        self.dx = dx_i["dx"]
        self.dy = dx_i["dy"]
        self.dz = dx_i["dz"]
        self.local_field = self.dm.createLocalVector()
        self.g = self.dm.createGlobalVector()
        self.mass = mass
        mx, my, mz = self.dm.getSizes()
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
        field_[:] = numpy.random.random(field_.shape)
        g_[:] = self.mass**2
        (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
        # PETSc magic to turn managed distributed array self.local_field into a local,
        # ghosted, usable array
        lf = self.dm.getVecArray(self.local_field)
        # field is trilinear and goes from (0,0,0) at (-,-,-) to 2\pi at (+,+,+)
        # N.B. All x,y,z-things could be put into loops over indices 0,1,2 for easier
        # extendability and future development, but this is easier to read 
        Xs = self.phys["minx"] + self.dx*(xs+1)
        Xm = Xs + self.dx*(xe-xs-1)
        Ys = self.phys["miny"] + self.dy*(ys+1)
        Ym = Ys + self.dy*(ye-ys-1)
        Zs = self.phys["minz"] + self.dz*(zs+1)
        Zm = Zs + self.dz*(ze-zs-1)
        X,Y,Z = numpy.mgrid[Xs:Xm:(xe-xs)*1j,
                            Ys:Ym:(ye-ys)*1j,
                            Zs:Zm:(ze-zs)*1j]
        field_[:]=0.0
        #''' -snes_type ngs can deal with this initialiser! But is slow!
        field_[xs:xe,ys:ye,zs:ze] = numpy.pi*(X/self.phys["maxx"]+
                                              #Y/self.phys["maxy"]+
                                              #Z/self.phys["maxz"]+2
                                              +1)/(1+
                                                   #2
                                                   0)
        #'''
        # we know the solution in 1D case, so init with it...
        #field_[:,0,0] = 4*numpy.arctan(numpy.exp(X[:,0,0]))
        #field_[self.dm.getSizes()[0]//2:,0,0] = 2*numpy.pi
        lf[xs-1,:,:]=0.0
        lf[xe,:,:]=2*numpy.pi
        lf[:,ys-1,:]=0.0
        lf[:,ye,:]=2*numpy.pi
        lf[:,:,zs-1]=0.0
        lf[:,:,ze]=2*numpy.pi
        
    def monitor(self, snes, iter, fnorm):
        sol = snes.getSolution()
        field_array = self.dm.getVecArray(sol)
    
    def rhs(self, snes, field, rhs):
        '''

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
        # get our array index ranges; note that these are GLOBAL, so cannot use python's
        # usual indexing like [-1]; we could get these also by calling the method
        # self.dm.getGhostCorners() or self.dm.getCorners()
        (xs, xe), (ys, ye), (zs, ze) = self.dm.getRanges()
        dx,dy,dz=self.dx,self.dy,self.dz
        # we need self.g as an array
        g_ = self.dm.getVecArray(self.g)
        # and it needs to be updated
        #g_[:,:,:] = self.mass**2*numpy.sin(field_array[xs:xe,ys:ye,zs:ze])
        # compute the Laplacian
        lapl = (
            (field_array[xs-1:xe-1,ys:ye,zs:ze]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs+1:xe+1,ys:ye,zs:ze])/dx*dy*dz +
            (field_array[xs:xe,ys-1:ye-1,zs:ze]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs:xe,ys+1:ye+1,zs:ze])/dy*dx*dz*0 +
            (field_array[xs:xe,ys:ye,zs-1:ze-1]-2*field_array[xs:xe,ys:ye,zs:ze]
             +field_array[xs:xe,ys:ye,zs+1:ze+1])/dz*dx*dy*0)
        # update the right hand side
        rhs_array[:,:,:] = (lapl[:,:,:] -
                            g_[:,:,:]*numpy.sin(field_array[xs:xe,ys:ye,zs:ze])*dx*dy*dz)
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
        print "jac"
        # two familiar calls
        self.dm.globalToLocal(X, self.local_field)
        field_array = self.dm.getVecArray(self.local_field)
        # we need self.g as an array
        g_ = self.dm.getVecArray(self.g)
        # this is not technically necessary if the non-zero structure does not change but
        # safer to set everything to zero anyway (can optimise later)
        P.zeroEntries()
        # Define that we want to update matrix using the FD stencil - there is no magic
        # here, PETSc just hides the if(on boundary) etc from us.
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
                    # I hope self.g, a.k.a. g_, has always been updated before we get here!
                    #diag = -2.0*(dx*dy/dz+dx*dz/dy+dy*dz/dx) - g_[i,j,k]*numpy.cos(u)*dx*dy*dz
                    diag = -2.0/dx - g_[i,j,k]*numpy.cos(u)*dx
                    # loop over the indices of ALL non-zero entries on this row and the
                    # values of the corresponding elements
                    for index, value in [
                            #((i,j,k-1), +1.0/dz*dx*dy),
                            #((i,j-1,k), +1.0/dy*dx*dz),
                            ((i-1,j,k), +1.0/dx*dy*dz),
                            ((i, j, k), diag),
                            ((i+1,j,k), +1.0/dx*dy*dz)
                            #,((i,j+1,k), +1.0/dy*dx*dz),
                            #((i,j,k+1), +1.0/dz*dx*dy)
                            ]:
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
# steady state sine-Gordon (or NLS?!?) equation...
# prepare the g(x,y) term
mass = OptDB.getScalar("mass", 1.0)
sineGordon = sineGordon(dm, {"dx":0.1, "dy":0.1e+1, "dz":0.1e+1}, mass)

# prepare the initial conditions
rhs = dm.createGlobalVector()

# go do fun things with sine-Gordon
# set up the SNES context
snes = PETSc.SNES().create()
snes.setDM(dm)
snes.setFunction(sineGordon.rhs, rhs)
snes.setMonitor(sineGordon.monitor)

# check  the interplay of -snes_mf, -snes_fd, and nothing at all! 
# PETSc has a complicated defaults system, so we deal with it here
# Normally you do not need to do this as you are only likely to use one or the other
# option but in this example we want them all.
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
    # this actually defaults to True but we want to make sure we have a way of
    # using the hand-written Jacobian, too and we want that by default
    fdcol=None
print("Using FD={fd}, MF={mf}, FD Color={fdcol}, MF Operator={mfop}".format(
    fd=fd, mf=mf, fdcol=fdcol, mfop=mfop))
if not((mf) or (mfop) or (fd) or (fdcol)):
    # No option was given, default to hand-written Jacobian EVEN THOUGH PETSc's internal
    # default in this case is -fd_color 1
    print("Using hand-written Jacobian with a preconditioner {prec}.".format(prec=snes.getKSP().getPC().getType()))
    J = dm.createMatrix()
    snes.setJacobian(sineGordon.formJacobian, J)
elif (mf or mfop):
    if (fd or fdcol):
        raise ValueError("Cannot have both MF and FD at the same time.")
elif (fd or fdcol or (fdcol==None)):
    # supplying no option means "-fd_color 1", so "fdcol==None" must be treated as
    # "fdcol==True"
    if (mf or mfop):
        raise ValueError("Cannot have both FD and MF at the same time.")


#--------------------------------------------------------------------------------
# finish the SNES setup
#--------------------------------------------------------------------------------
# decide which KSP to use (by default use CG)
snes.getKSP().setType("cg")
# set any -snes commend-line options (including those we checked above)
snes.setFromOptions()

# create an initial guess
field = dm.createGlobalVector()
sineGordon.create_initial_guess(field)

# have fun (and measure how long fun takes)
import cProfile
start = time.clock()
cProfile.run("snes.solve(None, field)")
end = time.clock()
# and plot
U = dm.createNaturalVector()
dm.globalToNatural(field, U)

# for debugging
lf_ = sineGordon.dm.getVecArray(sineGordon.local_field)
f_ = sineGordon.dm.getVecArray(field)
sol_ = sineGordon.dm.getVecArray(snes.getSolution())
rhs_ = sineGordon.dm.getVecArray(rhs)
# ouput some statistics
if (dm.getComm().getRank()==0):
    print("SNES Function evaluations: {iter} and final norm: {norm}; time spent solving: {time} s".format(
        iter=snes.getFunctionEvaluations(),
        norm=rhs.norm(),
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

