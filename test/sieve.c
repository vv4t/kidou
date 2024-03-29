void main()
{
  int prime[128];
  int n = 128;
  
  for (int i = 0; i < n; i++) {
    prime[i] = 1;
  }
  
  for (int p = 2; p * p < n; p++) {
    if (prime[p] > 0) {
      for (int i = p * p; i < n; i += p) {
        prime[i] = 0;
      }
    }
  }
  
  for (int i = 0; i < n; i++) {
    if (prime[i] > 0) {
      printf "%i", i;
    }
  }
}
