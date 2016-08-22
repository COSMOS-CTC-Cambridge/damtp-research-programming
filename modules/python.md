python
======

Please read the official [python tutorial](https://docs.python.org/2/tutorial/) (also have a look at [version 3 tutorial](https://docs.python.org/3/tutorial/index.html) to see how things will change in the future) to make sure your python is up to speed. In particular, you will should understand the basic syntax, modules, meaning of whitespece, how to use utf-8 encoding, how to deal with ' and " and linefeeds in strings.

Other useful features are operator overloading: `2*3+1==7`, but

``` {.python}
  'little bunny'+2*' foo'=='little bunny foo foo'
```

Slicing of arrays and strings
-----------------------------

This will be used heavily, so a few interactive examples TODO!!! some more array slicing examples and non-symmetric shapes and so forth. Check z301's notebook for details!

``` {.python}
  x="string"
  x
```

``` {.python}
  x[0]
```

``` {.python}
  x[-1]
```

``` {.python}
  x[2:-2]
```

numpy has some extra slicing features
-------------------------------------

First, let's see what a numpy array looks like: this is a 2x3x4 array.

``` {.python}
  import numpy
  skewed = numpy.random.random((2,3,4))
  skewed
```

We will use `array` in our examples later, we will initially create it as follows

``` {.python}
  array = numpy.arange(0,27)
  array
```

but now we give it a new shape

``` {.python}
  array=array.reshape(3,3,3)
  array
```

-   this is a slice

``` {.python}
  array[-1,:,1:]
```

-   and striding is also possible, and combining the two:

``` {.python}
  array[::2,:,2:0:-1]
```

-   numpy arrays have point-wise operator overloads:

``` {.python}
  array + array
```

``` {.python}
  array * array
```

-   nearly any imaginable mathematical function can operate on an array element-wise:

``` {.python}
  array ** 0.5
```

``` {.python}
  numpy.sinh(array)
```

-   but numpy matrices are bona fide matrices:

``` {.python}
  matrix=numpy.matrix(array[0,:,:])
  matrix*matrix
```

-   numpy matrices have all the basic operations defined, but not necessarily with good performance
-   for prototyping they're fine
-   **performance can be exceptional if numpy compiled suitably**
-   if you import `scipy` you have even more functions

``` {.python}
  import scipy
  import scipy.special
  scipy.special.kn(2,array)
```

-   I should say that

``` {.python}
  import scipy.fftpack
  scipy.fftpack.fftn(array)
```

-   performance of the FFT routines also depends on how everytihng was compiled
-   and theoretical physicists may find it amusing that numpy can do Einstein summation (and more)

``` {.python}
  numpy.einsum("iii", array)
```

``` {.python}
  numpy.einsum("ij,jk", array[0,:,:], array[1,:,:])
```

``` {.python}
  numpy.einsum("ijk,ljm", array, array)
```

Control flow statements
-----------------------

``` {.python}
  if (1>0):
    print("1 is indeed greater than 0")
  elif (1==0):
    print("Somehow 1 is equal to 0 now")
  else:
    print("Weird, 1 is somehow less than 0!")
```

``` {.python}
  for i in [0,1,2,3]:
    print(str(i))
  for i in range(4):
    print(str(i))
  for i in xrange(4):
    print(str(i))
```

``` {.python}
  for i in range(0,4): print(str(i))
```

``` {.python}
  print [i for i in range(0,4)]
  print [str(i) for i in range(0,4)]
  for i in range(4): print str(i)+","
  print ','.join([str(i) for i in range(0,4)])
```

-   there are others, but we won't use them

Section 5 of the tutorial is a must read
----------------------------------------

Section 9 describes python's classes and is a must, too
-------------------------------------------------------

