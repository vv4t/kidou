#include "sdl.h"
#include <SDL2/SDL.h>

static struct {
  vm_t *vm;
  SDL_Window *window;
  SDL_Renderer *renderer;
  int prev_time;
  int lag_time;
} sdl;

void line_f(vm_t *vm);
void cos_f(vm_t *vm);
void sin_f(vm_t *vm);

void sdl_init(vm_t *vm)
{
  sdl.window = NULL;
  sdl.renderer = NULL;
  sdl.vm = vm;
}

void sdl_window(int width, int height)
{
  if (SDL_Init(SDL_INIT_VIDEO) < 0) {
    printf("SDL_Error: %s\n", SDL_GetError());
    return;
  }
  
  sdl.window = SDL_CreateWindow(
    "kidou",
    SDL_WINDOWPOS_CENTERED,
    SDL_WINDOWPOS_CENTERED,
    width,
    height,
    SDL_WINDOW_OPENGL | SDL_WINDOW_SHOWN
  );
  
  sdl.renderer = SDL_CreateRenderer(sdl.window, -1, SDL_RENDERER_ACCELERATED | SDL_RENDERER_TARGETTEXTURE);
  
  vm_syscall_bind(sdl.vm, 2, line_f);
  vm_syscall_bind(sdl.vm, 3, cos_f);
  vm_syscall_bind(sdl.vm, 4, sin_f);
  
  sdl.prev_time = SDL_GetTicks();
  sdl.lag_time = 0;
}

bool sdl_exec()
{
  if (!sdl.window) {
    return false;
  }
  
  SDL_Event event;
  while (SDL_PollEvent(&event)) {
    switch (event.type) {
    case SDL_QUIT:
      SDL_DestroyRenderer(sdl.renderer);
      SDL_DestroyWindow(sdl.window);
      SDL_Quit();
      sdl.window = NULL;
      sdl.renderer = NULL;
      return false;
    }
  }
  
  int now_time = SDL_GetTicks();
  int delta_time = now_time - sdl.prev_time;
  sdl.prev_time = now_time;
  sdl.lag_time += delta_time;
  
  if (sdl.lag_time > 0) {
    SDL_RenderPresent(sdl.renderer);
    SDL_SetRenderDrawColor(sdl.renderer, 0, 0, 0, 255);
    SDL_RenderClear(sdl.renderer);
    SDL_SetRenderDrawColor(sdl.renderer, 255, 255, 255, 255);
    vm_call(sdl.vm, "draw");
  }
  
  while (sdl.lag_time > 0) {
    sdl.lag_time -= 15;
  }
  
  return true;
}

void line_f(vm_t *vm)
{ 
  int x0 = vm_arg_int(vm);
  int y0 = vm_arg_int(vm);
  int x1 = vm_arg_int(vm);
  int y1 = vm_arg_int(vm);

  SDL_RenderDrawLine(sdl.renderer, x0, y0, x1, y1);
}

void cos_f(vm_t *vm)
{
  float t = vm_arg_float(vm);
  vm_return_float(vm, cos(t));
}

void sin_f(vm_t *vm)
{
  float t = vm_arg_float(vm);
  vm_return_float(vm, sin(t));
}
