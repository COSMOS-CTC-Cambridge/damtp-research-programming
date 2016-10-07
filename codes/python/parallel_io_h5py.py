
from mpi4py import MPI
import h5py
import tempfile
import os
fn=tempfile.NamedTemporaryFile(dir="../codes/python/", prefix="hdf5_visualisation_example", suffix=".h5", delete=False)
fn.close()
rank = MPI.COMM_WORLD.rank
f = h5py.File(fn.name, 'w', driver='mpio', comm=MPI.COMM_WORLD)
dset = f.create_dataset('test', (4,), dtype='i')
dset[rank] = rank
f.close()
os.unlink(fm.name)
