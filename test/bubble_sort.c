#define n 512

int rand() syscall(6);

void main()
{
  int data[n];
  
  for (int i = 0; i < n; i++) {
    data[i] = rand();
  }
  
  for (int i = 0; i < n; i++) {
    for (int j = 0; j < n - i - 1; j++) {
      if (data[j] > data[j + 1]) {
        int tmp = data[j];
        data[j] = data[j + 1];
        data[j + 1] = tmp;
      }
    }
  }
  
  for (int i = 0; i < n; i += 1) {
    printf "%i", data[i];
  }
}
