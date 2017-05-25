import doctest
import numpy
import time
import datetime
import matplotlib
import matplotlib.pyplot
import scipy
import scipy.signal

def initial(size=(5,5)):
    '''Initialise the Game of Life to a random state.

    Doctests

    >>> state = initial(size=(3,7))
    >>> type(state),state.dtype,state.shape
    (<class 'numpy.ndarray'>, dtype('int64'), (3, 7))
    '''
    cells = numpy.random.randint(0,2,size)
    return cells

def step(cells):
    '''Take one Game of Life step.

    Doctests
    >>> step(numpy.array([[1, 0, 0, 1, 1, 0, 0],[0, 0, 0, 1, 0, 0, 0],[0, 0, 0, 1, 0, 1, 1],[1, 0, 0, 0, 0, 1, 1],[0, 0, 0, 0, 0, 0, 0],[0, 0, 0, 0, 0, 0, 0]]))
    array([[0, 0, 0, 1, 1, 0, 0],
           [0, 0, 1, 1, 0, 1, 1],
           [1, 0, 0, 0, 0, 1, 0],
           [1, 0, 0, 0, 1, 1, 0],
           [0, 0, 0, 0, 0, 0, 1],
           [0, 0, 0, 0, 0, 0, 0]])
    '''
    convolvemask = numpy.ones((3,3), dtype=numpy.int)
    convolvemask[1,1] = 0
    Nlive = scipy.signal.convolve2d(cells,convolvemask, mode='same', boundary="wrap")
    newcells = numpy.where(cells==1,
                           numpy.where(Nlive<2,0,numpy.where(Nlive>3,0,1)),
                           numpy.where(Nlive==3,1,0))
    return newcells

def run_game(size=(5,5)):
    cells = initial(size)
    print(cells)
    starttime = datetime.datetime.utcnow()
    while (starttime + datetime.timedelta(seconds=10) > datetime.datetime.utcnow()):
        cells = step(cells)
        print(cells)
        time.sleep(0.5)
    return
