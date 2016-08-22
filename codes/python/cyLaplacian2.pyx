
import cython,numpy
cimport numpy
DTYPE=numpy.float64
ctypedef numpy.float64_t DTYPE_t
@cython.boundscheck(False)
@cython.cdivision(True)
def cyLaplacian2(numpy.ndarray[DTYPE_t, ndim=3] data, numpy.ndarray[DTYPE_t, ndim=3] lapl,
                 numpy.ndarray[DTYPE_t, ndim=1] d):
    cdef double dx2
    cdef double dy2
    cdef double dz2
    dx2 = 1./(d[0]*d[0])
    dy2 = 1./(d[1]*d[1])
    dz2 = 1./(d[2]*d[2])
    lapl[1:-1,1:-1,1:-1] = (
        (data[0:-2,1:-1,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[2:,1:-1,1:-1])*dx2 +
        (data[1:-1,0:-2,1:-1] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,2:,1:-1])*dy2 +
        (data[1:-1,1:-1,0:-2] - 2*data[1:-1,1:-1,1:-1] + data[1:-1,1:-1,2:])*dz2)
    return
