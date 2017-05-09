import doctest
import numpy
import time
import datetime
import matplotlib
import matplotlib.pyplot
import matplotlib.animation

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
    newcells = numpy.copy(cells)
    maxx, maxy = cells.shape[0], cells.shape[1]
    for jj in range(maxy):
        for ii in range(maxx):
            # rule 5 is accounted for by the modulo operators
            # for parallel code MODULO IS EVIL
            living_neighbours = (cells[(ii+1)%maxx,(jj+1)%maxy] +
                                 cells[(ii+1)%maxx,(jj+0)%maxy] +
                                 cells[(ii+1)%maxx,(jj-1)%maxy] +
                                 cells[(ii+0)%maxx,(jj+1)%maxy] +
                                 cells[(ii+0)%maxx,(jj-1)%maxy] +
                                 cells[(ii-1)%maxx,(jj+1)%maxy] +
                                 cells[(ii-1)%maxx,(jj+0)%maxy] +
                                 cells[(ii-1)%maxx,(jj-1)%maxy]
                                 )
            if (cells[ii,jj] == 1):
                # this is a living cell
                if (living_neighbours < 2):
                    # rule 1
                    newcells[ii,jj] = 0
                elif (living_neighbours > 3):
                    # rule 3
                    newcells[ii,jj] = 0
                else:
                    # rule 2 is a no-op: we are already alive
                    pass
            else:
                # this is a dead cell
                if (living_neighbours == 3):
                    # rule 4
                    newcells[ii,jj] = 1
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
