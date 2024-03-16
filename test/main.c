float fib(float n)
{
  if (n < 2.0) {
    return 1.0;
  } else {
    return fib(n - 1.0) + fib(n - 2.0);
  }
}

void main()
{
  for (int i = 0; i < 10; i += 1) {
    printf "%i", i += 1;
  }
}
