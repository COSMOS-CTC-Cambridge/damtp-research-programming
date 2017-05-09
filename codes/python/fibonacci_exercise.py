def fib(n):
    '''
    Unit tests with doctest module
    >>> fib(0)
    []
    >>> fib(1)
    [1]
    >>> fib(2)
    [1, 1]
    >>> fib(3)
    [1, 1, 2]
    >>> fib(-1)
    []
    '''
    fibn=[1]*min(n,2)
    for i in range(2,n):
        fibn.append(fibn[-2]+fibn[-1])
    return fibn

def split_to_lines(inlist):
    '''
    Split a list to strings of no more than 80 characters each.

    Unit tests using doctest

    >>> split_to_lines(fib(31))
    ['1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987, 1597, 2584, 4181,', '6765, 10946, 17711, 28657, 46368, 75025, 121393, 196418, 317811, 514229, 832040,', '1346269']
    '''
    sep=", "
    inlist=sep.join([str(x) for x in inlist])
    lines=[]
    start=0
    while (start<len(inlist)):
        newstart=inlist[start:start+80].rfind(",")
        if (newstart == -1):
            newstart = len(inlist)
        else:
            if (len(inlist[start:start+80])<80):
                newstart=len(inlist)
            else:
                newstart = start + newstart + len(sep)
        lines.append(inlist[start:newstart].strip())
        start=newstart
    return lines

def print80(inlist):
    print("\n".join(split_to_lines(inlist)))
    return
