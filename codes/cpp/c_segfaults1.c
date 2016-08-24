
#include <stdio.h>

int main(int argc, char * argv[]) {
  int input1, input2;
  FILE *fptr;
  fptr = fopen("../codes/cpp/subdir1/input.dat","r");
  fread(&input1, sizeof(int), 1, fptr);
  fclose(fptr);
  fptr = fopen("../codes/cpp/subdirO/input.dat","r");
  fread(&input2, sizeof(int), 1, fptr);
  fclose(fptr);
  printf("%i + %i = %i\n", input1, input2, input1+input2);
  return 0;
}
