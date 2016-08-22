#include <iostream>
#include <mpi.h>
#include <assert.h>

int main(int argc, char* argv[]) {
  MPI_Init(&argc, &argv);

  int rank, size;
  assert(MPI_Comm_rank(MPI_COMM_WORLD, &rank)==0);
  assert(MPI_Comm_size(MPI_COMM_WORLD, &size)==0);
    
  std::cout << "Hello, World. I am rank " <<  rank
            << " of your MPI communicator of " << size
            << " ranks." << std::endl;

  MPI_Finalize();

  return 0;
}
