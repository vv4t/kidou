#include "file.h"

#include <stdio.h>
#include <stdlib.h>

char *file_read_all(const char *path)
{
  FILE *f = fopen(path, "rb");
  
  if (!f) {
    perror(path);
    return NULL;
  }
  
  fseek(f, 0, SEEK_END);
  long fsize = ftell(f);
  fseek(f, 0, SEEK_SET);
  
  char *buffer = malloc(fsize + 1);
  fread(buffer, fsize, 1, f);
  fclose(f);
  
  buffer[fsize] = 0;
  
  return buffer;
}
