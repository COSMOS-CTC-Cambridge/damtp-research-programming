#!/usr/bin/env python3
import mpi4py
from mpi4py import MPI
size=MPI.COMM_WORLD.Get_size()
print("Hello, World. I am rank "+
      "{rank: 0{len}d} of your MPI communicator of {size} ranks".format(
      rank=MPI.COMM_WORLD.Get_rank(),
      len=len(str(size)),
      size=size))
