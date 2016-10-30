
import ipyparallel
c = ipyparallel.Client(profile="mpi", cluster_id="training_cluster_0")

c[:].execute("import numpy").wait()
if not("numpy" in dir()): print("No numpy here!")
with c[:].sync_imports():
    import scipy
if ("scipy" in dir()): print("scipy here!")

# We need to load numpy also on frontend
import numpy
data = numpy.random.random(18)
c[:].map_sync(lambda x:x+1, data)

c[:2].map_sync(lambda x:x+1, data)

c[1:3].map_sync(lambda x:x+1, data)
