#include "lib/sdl.h"
#include "lib/math.h"

int x_c;
int y_c;

int u_c;
int v_c;

void main()
{
  x_c = 30;
  y_c = 30;
  u_c = 4;
  v_c = 4;
  
  window(640, 480);
}

void draw()
{
  x_c += u_c;
  y_c += v_c;
  
  if (x_c - 15 < 0 || x_c + 15 > 640)
    u_c = -u_c;
  
  if (y_c - 15 < 0 || y_c + 15 > 480)
    v_c = -v_c;
  
  circle(x_c, y_c , 15);
  circle(x_c, y_c , 10);
  circle(x_c, y_c , 5);
}
