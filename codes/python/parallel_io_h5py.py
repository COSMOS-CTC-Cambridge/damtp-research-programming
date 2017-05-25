import mpi4py
from mpi4py import MPI
import h5py
import tempfile
import os
import array
if (MPI.COMM_WORLD.rank == 0):
    temp="hdf5_visualisation_example.h5"
    temp2=array.array("c","")
    temp2.fromstring(temp)
else:
    temp2=array.array("c", "\0")*1024
MPI.COMM_WORLD.Bcast([temp2, MPI.CHAR], root=0)   
KEEP_ME_AROUND = temp2.tostring()
rank = MPI.COMM_WORLD.rank
print KEEP_ME_AROUND                                                  
f = h5py.File(KEEP_ME_AROUND, "w", driver="mpio", comm=MPI.COMM_WORLD)
dset = f.create_dataset("test", (4,), dtype="f8")
dset[rank] = rank
f.close()
