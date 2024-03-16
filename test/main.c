struct thing {
  float x;
  float y;
};

void main()
{
  struct thing b;
  struct thing x = (struct thing) b;
  x.x = 3.0;
  
  printf "%f", x.x;
}
