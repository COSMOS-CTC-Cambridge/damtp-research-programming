#define _GNU_SOURCE 1
#define _POSIX_C_SOURCE 200809L
#define _XOPEN_SOURCE 700
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <time.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>


#define SIZE 1000*1000*100

int main(int argc, char *argv[]) {
  if (argc != 3)
    return 1;
  int fd1 = open(argv[1], O_WRONLY|O_TRUNC|O_CREAT, S_IRUSR|S_IWUSR);
  int fd2 = open(argv[2], O_WRONLY|O_TRUNC|O_CREAT, S_IRUSR|S_IWUSR);
  double *data = (double *) calloc(SIZE, sizeof(double));
  struct timespec t1, t2, t3;
  clock_gettime(CLOCK_MONOTONIC, &t1);
  for (int i=0; i<SIZE; i++) {
    write(fd1, data+i, sizeof(double)*1);
  }
  clock_gettime(CLOCK_MONOTONIC, &t2);
  write(fd2, data, sizeof(double)*SIZE);
  clock_gettime(CLOCK_MONOTONIC, &t3);
  printf("Writing one element at a time took %6li seconds\n", t2.tv_sec-t1.tv_sec);
  printf("Writing all elements at once took  %6li seconds\n", t3.tv_sec-t2.tv_sec);
  close(fd1);
  close(fd2);
  return 0;
}
