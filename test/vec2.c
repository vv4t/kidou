struct vec2 {
  int x;
  int y;
};

struct vec2 vec2(int x, int y)
{
  struct vec2 v;
  v.x = x;
  v.y = y;
  return v;
}

struct vec2 add(struct vec2 a, struct vec2 b)
{
  struct vec2 c;
  c.x = a.x + b.x;
  c.y = a.y + b.y;
  return c;
}

void main()
{
  struct vec2 a = vec2(3, 4);
  struct vec2 b = vec2(5, 6);
  struct vec2 c = add(a, b);
  
  print_int c.x;
  print_int c.y;
}
