#include "sdl.h"
#include "math.h"

float t = 0.0;

void main()
{
  window(640, 480);
}

void draw()
{
  int x = 640/2 + (int) (cos(t) * 40.0);
  int y = 480/2 + (int) (sin(t) * 40.0);
  
  line(640/2, 480/2, x, y);
  
  t += 0.15;
}
