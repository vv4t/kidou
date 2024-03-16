#ifndef SDL_H
#define SDL_H

void window(int width, int height) syscall(1);
void line(int x0, int x1, int y0, int y1) syscall(2);

#endif
