#define TEST 3

#include "test.h"

void main()
{
  for (int i = 0; i < TEST; i += 1) {
    #ifdef TEST
    printf "hi";
    #endif
    printf "ok";
  }
}
