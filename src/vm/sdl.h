#ifndef SDL_H
#define SDL_H

#include "vm.h"
#include <stdbool.h>

void sdl_init(vm_t *vm);
void sdl_window(int width, int height);
bool sdl_exec();

#endif
