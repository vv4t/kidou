void main()
{
  int n = 5;
  
  int data[5];
  
  data[0] = 10;
  data[1] = 1;
  data[2] = 234;
  data[3] = 5;
  data[4] = 4;
  
  for (int i = 0; i < n; i += 1) {
    for (int j = 0; j < n - i - 1; j += 1) {
      if (data[j] > data[j + 1]) {
        int tmp = data[j];
        data[j] = data[j + 1];
        data[j + 1] = tmp;
      }
    }
  }
  
  for (int i = 0; i < n; i += 1) {
    print_int data[i];
  }
}
