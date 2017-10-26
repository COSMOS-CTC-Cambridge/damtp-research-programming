@directview.remote(block=False)
def sendrecv():
    import mpi4py
    from mpi4py import MPI
    import numpy
    databuf = numpy.random.random(5)
    recvbuf = numpy.zeros_like(databuf)
    recv=MPI.COMM_WORLD.Irecv(buf=[recvbuf, databuf.shape[0], MPI.DOUBLE], source=MPI.COMM_WORLD.Get_rank() ^ 0x1, tag=42)
    send=MPI.COMM_WORLD.Isend(buf=[databuf, databuf.shape[0], MPI.DOUBLE], dest=MPI.COMM_WORLD.Get_rank() ^ 0x1, tag=42)
    error=MPI.Request.Waitall([send,recv])
    for rank in range(0,MPI.COMM_WORLD.Get_size()):
        if (MPI.COMM_WORLD.Get_rank() == rank):
            print("I, rank {}, sent\n".format(rank), databuf, "\nand received\n", recvbuf)
    return
ret=sendrecv()
ret.wait()
ret.display_outputs()
