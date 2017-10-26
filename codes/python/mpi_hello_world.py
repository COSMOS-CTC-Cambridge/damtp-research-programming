import ipyparallel as ipp
c = ipp.Client(profile="mpi", cluster_id="training_cluster_0")
c.ids
directview=c[:]
directview.execute("import mpi4py").wait()
directview.execute("from mpi4py import MPI").wait()

res1=directview.map(
    lambda data: "Hello, World. I am rank "+
    "{rank: 0{len}d} of your MPI communicator of {size} ranks and was sent data {d}".format(
        rank=MPI.COMM_WORLD.Get_rank(),
        len=len(str(MPI.COMM_WORLD.Get_size())),
        size=MPI.COMM_WORLD.Get_size(), d=str(data)),
        data)
lista = [x for x in res1.result()]
for output in lista: print(output)

res1=directview.map(
    lambda data: "Hello, World. I am rank "+
    "{rank: 0{len}d} of your MPI communicator of {size} ranks and was sent data:\n{d}".format(
        rank=MPI.COMM_WORLD.Get_rank(),
        len=len(str(MPI.COMM_WORLD.Get_size())),
        size=MPI.COMM_WORLD.Get_size(), 
        d=data),
        data)
lista = [x for x in res1.result()]
for output in lista: print(output)
