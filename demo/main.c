#include "lib/sdl.h"
#include "lib/math.h"
#include "lib/cirno.h"

struct mat4 mat_view;
struct mat4 mat_project;
struct mat4 mat_vp;

void _circle(struct vec4 p, float r)
{
  circle((int) p.x, (int) p.y, (int) r);
}

void _line(struct vec4 x, struct vec4 y)
{
  struct vec4 Ax = mulv(mat_vp, x);
  struct vec4 Ay = mulv(mat_vp, y);
  
  struct vec4 u = mulf(Ax, 1.0 / Ax.w);    
  struct vec4 v = mulf(Ay, 1.0 / Ay.w);
  
  if (Ax.z > 2.0 && Ay.z > 2.0) {
    line((int) u.x, (int) u.y, (int) v.x, (int) v.y);
  }
}

float t;

void main()
{
  t = 0.0;
  
  mat_project = mat4(
    vec4(320.0, 0.0, 320.0, 0.0),
    vec4(0.0, -240.0, 240.0, 0.0),
    vec4(0.0, 0.0, 1.0, 0.0),
    vec4(0.0, 0.0, 1.0, 0.0)
  );
  
  window(640, 480);
}

void draw()
{
  t += 0.015;
  
  mat_view = translate(vec3(0.0, 0.0, cos(t) * 3.0));
  mat_vp = mulm(mat_project, mat_view);
  
  for (float i = -4.0; i <= 4.0; i += 0.5) {
    for (float j = 4.0; j <= 10.0; j += 0.5) {
      _line(vec3(i, -1.0, j), vec3(i + 1.0, -1.0, j));
      _line(vec3(i, -1.0, j), vec3(i, -1.0, j + 1.0));
    }
  }
}
