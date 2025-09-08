#include <SDL2/SDL.h>
#include <iostream>
Uint8 r = 255, g = 0, b = 127; 

int main() {
    SDL_Init(SDL_INIT_EVERYTHING);
    SDL_Window* window = SDL_CreateWindow("Assignment 01", SDL_WINDOWPOS_CENTERED,
                        SDL_WINDOWPOS_CENTERED, 800, 600, SDL_WINDOW_SHOWN);
    SDL_Renderer* renderer = SDL_CreateRenderer(window, -1,
                        SDL_RENDERER_ACCELERATED);
    bool run = true;
    SDL_Event event;
    while (run==true){
        while (SDL_PollEvent(&event)) {
            if (event.type == SDL_QUIT)
                run = false;
            else if (event.type == SDL_MOUSEBUTTONDOWN) {
                if (r > 8)  r -=8;
                else    r = 0;
                if (b > 4)  b -= 4;
                else    b = 0;
            }
        }
        SDL_SetRenderDrawColor(renderer, r, g, b, 255);
        SDL_RenderClear(renderer);
        SDL_RenderPresent(renderer);
    }
    SDL_DestroyRenderer(renderer);
    SDL_DestroyWindow(window);
    SDL_Quit();
    return 0;
}