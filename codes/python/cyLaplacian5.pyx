import cython,numpy
cimport numpy
DTYPE=numpy.float64
ctypedef numpy.float64_t DTYPE_t
@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
def cyLaplacian5(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl, numpy.ndarray[DTYPE_t, ndim=1] d, int N):
    cdef int xmax = data.shape[0]
    cdef int ymax = data.shape[1]
    cdef int zmax = data.shape[2]
    cdef double dx2 = 1./(d[0]*d[0])
    cdef double dy2 = 1./(d[1]*d[1])
    cdef double dz2 = 1./(d[2]*d[2])
    cdef int ii, jj, kk
    for ii in range(1,xmax-1):
        for jj in range(1,ymax-1):

            for kk in range(1,zmax-1):
                lapl[ii,jj,kk] = (
                    (data[ii-1,jj,kk] - 2*data[ii,jj,kk] + data[ii+1,jj,kk])*dx2 +
                    (data[ii,jj-1,kk] - 2*data[ii,jj,kk] + data[ii,jj+1,kk])*dy2 +
                    (data[ii,jj,kk-1] - 2*data[ii,jj,kk] + data[ii,jj,kk+1])*dz2)
    return
