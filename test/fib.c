int fib(int n)
{
  if (n < 2) {
    return 1;
  } else {
    return fib(n - 1) + fib(n - 2);
  }
}

void main()
{
  for (int i = 0; i < 10; i += 1) {
    print_int fib(i);
  }
}
