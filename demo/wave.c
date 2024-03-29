#include "lib/math.h"
#include "lib/sdl.h"

#define NUM_BOB 64

struct bob {
  float u;
  float u_t;
};

struct bob bob_arr[NUM_BOB];

void main()
{
  window(640, 480);
  
  bob_arr[0].u = 0.0;
  bob_arr[0].u_t = 0.0;
  
  for (int i = 0; i <= 5; i++) {
    bob_arr[i + 1].u = 10.0;
    bob_arr[i + 1].u_t = 10.0;
  }
  
  for (int i = 0; i <= 5; i++) {
    bob_arr[i + 30].u = 10.0;
    bob_arr[i + 30].u_t = 10.0;
  }
}

void draw()
{
  for (int i = 1; i < NUM_BOB- 1; i++) {
    float du_dx_1 = bob_arr[i + 1].u - bob_arr[i].u;
    float du_dx_2 = bob_arr[i].u - bob_arr[i - 1].u;
    
    float d2u_dx2 = du_dx_1 - du_dx_2;
    
    bob_arr[i].u_t += d2u_dx2;
  }
  
  for (int i = 0; i < NUM_BOB; i++) {
    bob_arr[i].u += bob_arr[i].u_t;
  }
  
  for (int i = 0; i < NUM_BOB; i++) {
    circle(
      320 - NUM_BOB * 5 + i * 10,
      240 + (int) bob_arr[i].u,
      5
    );
  }
  
  for (int i = 1; i < NUM_BOB; i++) {
    line(
      320 - NUM_BOB * 5 + (i - 1) * 10,
      240 + (int) bob_arr[i - 1].u,
      320 - NUM_BOB * 5 + i * 10,
      240 + (int) bob_arr[i].u
    );
  }
}
