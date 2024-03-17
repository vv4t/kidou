#define n 512

int rand() syscall(5);

void main()
{
  int data[n];
  
  for (int i = 0; i < n; i += 1) {
    data[i] = rand();
  }
  
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
    printf "%i", data[i];
  }
}
