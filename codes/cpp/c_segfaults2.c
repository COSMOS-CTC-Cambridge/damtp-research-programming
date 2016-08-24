
#include <stdlib.h>
double * invert_data(int sz) {
  double dest[20] = {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19};
  double * data = (double *) calloc(20,sizeof(double));
  // [data] [sz] [*dest0 [*dest+1] ... [*dest+19]
  for (int ii=0; ii<=sz; ++ii) {
    dest[10+ii] = data[ii]+1;
  }
  return data;
}
  
int main(int argc, char * argv[]) {
  double *data = invert_data(10);
  free(data);
  return 0;
}
