struct vec4 {
  float x;
  float y;
  float z;
  float w;
};

struct mat4 {
  float m[16];
};

struct vec4 vec2(float x, float y)
{
  struct vec4 v;
  v.x = x;
  v.y = y;
  v.z = 0.0;
  v.w = 1.0;
  return v;
}

struct vec4 vec3(float x, float y, float z)
{
  struct vec4 v;
  v.x = x;
  v.y = y;
  v.z = z;
  v.w = 1.0;
  return v;
}

struct vec4 vec4(float x, float y, float z, float w)
{
  struct vec4 v;
  v.x = x;
  v.y = y;
  v.z = z;
  v.w = w;
  return v;
}

struct mat4 mat4(struct vec4 a, struct vec4 b, struct vec4 c, struct vec4 d)
{
  struct mat4 m;
  m.m[0] = a.x; m.m[4] = b.x; m.m[8] = c.x;   m.m[12] = d.x;
  m.m[1] = a.y; m.m[5] = b.y; m.m[9] = c.y;   m.m[13] = d.y;
  m.m[2] = a.z; m.m[6] = b.z; m.m[10] = c.z;  m.m[14] = d.z;
  m.m[3] = a.w; m.m[7] = b.w; m.m[11] = c.w;  m.m[15] = d.w;
  return m;
}

struct mat4 translate(struct vec4 v)
{
  return mat4(
    vec4(1.0, 0.0, 0.0, v.x),
    vec4(0.0, 1.0, 0.0, v.y),
    vec4(0.0, 0.0, 1.0, v.z),
    vec4(0.0, 0.0, 0.0, 1.0)
  );
}

struct mat4 rotate_y(float t)
{
  float c = cos(t);
  float s = sin(t);
  
  return mat4(
    vec4(c, 0.0, -s, 0.0),
    vec4(0.0, 1.0, 0.0, 0.0),
    vec4(s, 0.0, c, 0.0),
    vec4(0.0, 0.0, 0.0, 1.0)
  );
}

struct vec4 add(struct vec4 a, struct vec4 b)
{
  return vec4(
    a.x + b.x,
    a.y + b.y,
    a.z + b.z,
    a.w + b.w
  );
}

struct vec4 mulf(struct vec4 v, float f)
{
  return vec4(
    v.x * f,
    v.y * f,
    v.z * f,
    v.w * f
  );
}

struct mat4 mulm(struct mat4 a, struct mat4 b)
{
  struct mat4 c;
  for (int i = 0; i < 4; i++) {
    for (int j = 0; j < 4; j++) {
      c.m[i * 4 + j] =  a.m[i * 4 + 0] * b.m[0 * 4 + j]
                      + a.m[i * 4 + 1] * b.m[1 * 4 + j]
                      + a.m[i * 4 + 2] * b.m[2 * 4 + j]
                      + a.m[i * 4 + 3] * b.m[3 * 4 + j];
    }
  }
  
  return c;
}

struct vec4 mulv(struct mat4 m, struct vec4 v)
{
  return vec4(
    m.m[0] * v.x + m.m[1] * v.y + m.m[2] * v.z + m.m[3] * v.w,
    m.m[4] * v.x + m.m[5] * v.y + m.m[6] * v.z + m.m[7] * v.w,
    m.m[8] * v.x + m.m[9] * v.y + m.m[10] * v.z + m.m[11] * v.w,
    m.m[12] * v.x + m.m[13] * v.y + m.m[14] * v.z + m.m[15]* v.w
  );
}
