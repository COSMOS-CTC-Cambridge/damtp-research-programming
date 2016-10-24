
directview.execute("import numpy")

@directview.parallel(block=True)
def greduce(localval):
    localval = numpy.array(localval)
    redsum = numpy.zeros_like(localval)*numpy.nan
    MPI.COMM_WORLD.Reduce([localval, MPI.DOUBLE], [redsum, MPI.DOUBLE], op=MPI.SUM, root=0)
    return redsum
def greduce_noMPI(gobalval):
    return reduce(lambda x,y:x+y, local_map_noMPI, 0)

@directview.parallel(block=True)
def lmap(data):
    sum = numpy.array(data).sum() 
    return sum

@directview.remote(block=True)
def get_data():
    len = 1e7
    loclen = numpy.ceil(len*1.0/MPI.COMM_WORLD.Get_size())
    myrank=MPI.COMM_WORLD.Get_rank()
    return numpy.arange(loclen*myrank, min(len,loclen*(1+myrank)))
@directview.parallel(block=True)
def get_data_noMPI(myinput):
    len = 1e7
    loclen = numpy.ceil(len*1.0/myinput[0][0])
    myrank=myinput[0][1]
    return numpy.arange(loclen*myrank, min(len,loclen*(1+myrank)))

input_data=get_data()
input_data_noMPI=get_data_noMPI([ [len(directview.targets),i] for i in range(0,len(directview.targets))])
local_map=lmap(input_data)
local_map_noMPI=lmap(input_data_noMPI)
global_reduce=greduce(local_map)
global_reduce_noMPI=greduce_noMPI(local_map_noMPI)
print(global_reduce, global_reduce_noMPI)
