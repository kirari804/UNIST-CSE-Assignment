#include <iostream>
#include "shape.h"
using namespace std;

double area_of_shape(shape const& s) {
    return s.area();
}

double area_of_all_shape(shape const* const* shapes, size_t n) {
    double total = 0;
    for (size_t i=0; i<n; i++) {
        total += shapes[i]->area();
    }
    return total;
 
 }
int main() {
    triangle t(1,4);
    circle c = 5;
    square s=4;
    shape* ss[] = {&t, &c, &s}; //array of pointers
    cout << area_of_all_shape(ss, 3)  <<endl;
 }