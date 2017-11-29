%load_ext Cython

%%cython --compile-args=-Ofast --compile-args=-fopenmp --link-args=-fopenmp --link-args=-lgomp
import cython,numpy,os
from cython.parallel import prange, parallel, threadid
cimport numpy
DTYPE=numpy.float64
ctypedef numpy.float64_t DTYPE_t
@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
def test_unsafe(double [::1] test, int num_threads):
    cdef int xmax = test.shape[0], ii, jj
    cdef double[:] blergh=numpy.zeros(10)
    with nogil, parallel(num_threads=num_threads):
        for ii in prange(0,xmax,schedule="static", chunksize=1):
            for jj in range(0,10):
                blergh[jj] = blergh[jj] + test[ii]
    return numpy.asarray(blergh)

%%cython --compile-args=-Ofast --compile-args=-fopenmp --link-args=-fopenmp --link-args=-lgomp
import cython,numpy,os
from cython.parallel cimport prange, parallel, threadid
cimport numpy
DTYPE=numpy.float64
ctypedef numpy.float64_t DTYPE_t
@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
def test_safe(double [::1] test, int num_threads):
    cdef int xmax = test.shape[0], ii, jj, mytid
    cdef double[:,:] blergh=numpy.zeros((num_threads,10))
    cdef double[:] blerghsum=numpy.zeros(10)
    with nogil, parallel(num_threads=num_threads):
        mytid = threadid()
        for ii in prange(0,xmax,schedule="static", chunksize=1):
            for jj in range(0,10):
                blergh[mytid,jj] += test[ii]
    return numpy.asarray(blergh).sum(axis=0)

data = numpy.ones(1000000)
%timeit test_unsafe(data,1)
%timeit test_unsafe(data,2)
%timeit test_unsafe(data,4)
%timeit test_unsafe(data,8)
%timeit test_safe(data,1)
%timeit test_safe(data,2)
%timeit test_safe(data,4)
%timeit test_safe(data,8)

testdata=numpy.array([2,3,5,7,11,13,17,19,23,31],dtype="f8")
res = test_safe(testdata,8)
print("We expect ", res)
ii = 0
while True or ii<1000000:
     res2 = test_unsafe(testdata,2)
     ii = ii + 1
     if numpy.allclose(res,res2):
          continue
     else:
          raise ValueError("WRONG", res2)

%%cython --compile-args=-Ofast --compile-args=-fopenmp --link-args=-fopenmp --link-args=-lgomp
import cython,numpy,os
from cython.parallel cimport prange, parallel, threadid
cimport numpy
DTYPE=numpy.float64
ctypedef numpy.float64_t DTYPE_t
@cython.boundscheck(False)
@cython.cdivision(True)
@cython.wraparound(False)
def test_safe_fast(double [::1] test, int num_threads):
    cdef int xmax = test.shape[0], ii, jj, mytid
    cdef double[:,:] blergh=numpy.zeros((num_threads,16))
    cdef double[:] blerghsum=numpy.zeros(10)
    with nogil, parallel(num_threads=num_threads):
        mytid = threadid()
        for ii in prange(0,xmax,schedule="static", chunksize=1):
            for jj in range(0,10):
                blergh[mytid,jj] += test[ii]
    return numpy.asarray(blergh).sum(axis=0)

%timeit test_safe_fast(data,1)
%timeit test_safe_fast(data,2)
%timeit test_safe_fast(data,4)
%timeit test_safe_fast(data,8)
