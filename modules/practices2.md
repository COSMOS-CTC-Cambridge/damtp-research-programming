Code Modularity
===============

-   a rule of thumb: *a single modular piece of code fits on screen all at the same time*
-   split code into different files appropriately
    -   in C/Fortran use a makefile to help compiling and linking them together
    -   in python, codes in separate files become *modules*
-   we'll see more of this once we start coding

Correctness Testing
===================

-   also try to get into the habit of always writing correctness tests of your routines
-   we'll look into this in detail later, but something like this will catch a simple typo

``` python
import doctest
def square_minus_one(x):
    '''Calculate x^2-1
    >>> square_minus_one(6.5)
    41.25
    '''
    return x*2-1

doctest.testmod()
```

-   let's fix that so we don't need to suffer this error report all the time

``` python
import doctest
def square_minus_one(x):
    '''Calculate x^2-1
    >>> square_minus_one(6.5)
    41.25
    '''
    return x**2-1

doctest.testmod()
```

-   but beware of floating point numbers, they may give you nasty surprises

``` python
def square(x):
    '''Calculate x^2
    >>> square(0.2)
    0.04
    '''
    return x**2

doctest.testmod()
```

-   most people would thing 0.2<sup>2</sup> = 0.04 but a computer might not
-   unfortunately no easy escape
    -   copy-pasting the funny number from an actual python shell is not guaranteed to work in another computer or even the same after a new version of python, C, system libraries etc (output details changed e.g. between python versions 3.1 and 3.2)
    -   and some routines might have random numbers in them: how to check those results?

Floating Point Number Comparisons
---------------------------------

-   these must always be done with some kind of tolerance

``` python
def square(x):
    '''Calculate x^2 - a fixed version
    >>> import numpy
    >>> abs(square(0.2)-0.04) < numpy.finfo(0.2).eps
    True
    '''
    return x**2

doctest.testmod()
```

-   do not worry about what `import numpy` is or means, we'll get to that
-   in this particular case, `numpy` actually has a convenient tolerance-aware comparison routine for us

``` python
def square(x):
    '''Calculate x^2 - a fixed version
    >>> import numpy
    >>> numpy.allclose(square(0.2),0.04)
    True
    '''
    return x**2

doctest.testmod()
```

-   random numbers are worse: you'll have to check their statistics are correct but that requires a lot of nubmers!
    -   not very nice: even 1000 samples from the standard distribution often gives means of 0.01 or so
    -   and even if your code is correct, it might fail every once in a while
    -   perhaps best solution is to test everything either with a constant seed or
    -   isolate random number generation to a very small routine and test everything else with non-random inputs
-   the [python tutorial](https://docs.python.org/3/tutorial/) has a lengthy explanation and discussion on issues related to the approximative nature of floating point numbers
-   compiled code may give even worse surprises
    -   *a* \* *b* − floor(*a* \* *b*)≥0 but not necessarily with floating points!
    -   has to do with assembler instructions: this turns into (in pseudocode)

        temp = multiply(a,b)
        temp = -floor(temp)
        result = fma(a,b,temp)

    -   the `fma(a,b,temp)` is a performance enhancing instruction which does `a*b+temp` in one instruction instead of saving `a*b` into another temporary variable and then adding to it
    -   but in an Intel compatible CPU (possibly others), the `fma` instruction uses higher precision in its internal multiplication and addition than the temporary variable is capable of representing
    -   unfortunately, no failsafe way out!
-   again, please do get into the practice of writing tests

Continuous Integration and Testing — a Quick Look
=================================================

-   the idea is that there is some automaton somewhere, which takes each commit (or specified branch HEADs at fixed times) and
    -   compiles it if relevant
    -   runs all unit tests
    -   installs onto a testbed platform (often a container or virtual machine)
    -   tests that the testbed works
    -   sometimes even deploys this into production
-   this is quite useful and not very hard to set up
-   in scientific computing, the last two or three steps are often impractical to implement
-   code modularity is especially useful here: no need to compile and test all modules, only the changed ones, a bit like `make` only rebuilds changes source code files
