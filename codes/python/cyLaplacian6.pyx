import cython,numpy,os
from cython.parallel import prange, parallel
cimport numpy
DTYPE=numpy.float64
ctypedef numpy.float64_t DTYPE_t
#@cython.profile(True)
#@cython.linetrace(True)
@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
def cyLaplacian6(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d, int N):
    cdef int xmax = data.shape[0]
    cdef int ymax = data.shape[1]
    cdef int zmax = data.shape[2]
    cdef int num_threads = N
    cdef double dx2 = 1./(d[0]*d[0])
    cdef double dy2 = 1./(d[1]*d[1])
    cdef double dz2 = 1./(d[2]*d[2])
    cdef int ii, jj, kk
    with nogil, parallel(num_threads=num_threads):
        for ii in prange(1,xmax-1,schedule="runtime"):
            for jj in xrange(1,ymax-1):
                for kk in xrange(1,zmax-1):
                    lapl[ii,jj,kk] = (
                        (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])*dx2 +
                        (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])*dy2 +
                        (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])*dz2)
    return
