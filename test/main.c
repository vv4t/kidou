struct thing {
  int a;
  int b;
};

void main()
{
  int i;
  for (i = 0; i < 20; i += 1) {
    if (i < 5) {
      print_int 5;
    } else if (i < 10) {
      print_int 10;
    } else if (i < 15) {
      print_int 15;
    } else {
      print_int 999;
    }
  }
}
