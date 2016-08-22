#!/usr/bin/env python

'''
TODO!!! Could we use doxygen or similar to convert docstrings to .org and thus avoid the
need to manually syncronise the code and the slides?
'''


'''This simply fills the non-ghosted part of the lattice with squares of consequtive
integers, stsrting from rank number, does the ghost exchange, computes gradients (2nd
order central differences) in the non-ghosted area, calculates maxima of local gradients,
and Allreduces the global maximum.

Along the way, it prints some diagnostics about the lattice and eventually of the
gradients.
'''

try:
    import ipyparallel
    c = ipyparallel.Client(profile="mpi")
    directview=c[:]
    directview.block=True
except IOError:
    try:
        del ipyparallel
    except:
        pass
    import mpi4py
    from mpi4py import MPI
except ImportError:
    try:
        del ipyparallel
    except:
        pass
    import mpi4py
    from mpi4py import MPI

if ("ipyparallel" in dir()):
    with directview.sync_imports():
        import sys
        import os
    MYDIR=os.path.dirname(os.path.realpath(__file__))
    directview.execute('sys.path.append("'+MYDIR+'")')
    with directview.sync_imports():
        import distributed_computing_worker
else:
    import distributed_computing_worker


if not("ipyparallel" in dir()):
    # fake decorator...
    class noop(object):
        def parallel(self, block=True):
            def passthrough(func):
                def callit(*args, **kwargs):
                    return func(*args, **kwargs)
                return callit
            return passthrough
        def remote(self, block=True):
            def passthrough(func):
                def callit(*args, **kwargs):
                    return func(*args, **kwargs)
                return callit
            return passthrough
        def apply_async(self, func, *args, **kwargs):
            return func(*args, **kwargs)
    directview=noop()


def main():
    me=distributed_computing_worker.rankinfo(sizes=[3,4,5])
    cartesian_topology=distributed_computing_worker.topology(me)
    ghosts = distributed_computing_worker.ghost_data(cartesian_topology, me.localsizes)
    cartesian_topology.print_info()
    local_array = distributed_computing_worker.initialise_values(me)
    result_l, result_g = distributed_computing_worker.find_max_grad(cartesian_topology, local_array, ghosts)
    distributed_computing_worker.serialised_print("Rank {rank} had max gradient {maxgrad_l} while the global was {maxgrad_g}."
                     .format(
                         rank=me.rank,
                         maxgrad_l=result_l,
                         maxgrad_g=result_g),
                     cartesian_topology.topology)
    if (me.rank == 0):
        if (distributed_computing_worker.testme(result_g, cartesian_topology)):
            print("Result is correct.")
        else:
            print("Result is incorrect!")
    return result_g, local_array

if (__name__ == "__main__"):
    la=directview.apply_async(main)
    try:
        la.wait()
        la.display_outputs()
    except:
        pass
