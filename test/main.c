void main()
{
  int a;
  int b;
  int *c = &a;
  b = *c = 4;
  // not this
  printf "%i %i", a, b;
}
