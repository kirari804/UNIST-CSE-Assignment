#include <iostream>
#include "growing_array.h"

growing_array::growing_array():
    elements(new int[0]), num_element(0) {}

growing_array::growing_array(growing_array const& other) 
    : elements(new int(other.num_element)) {}


void growing_array::append(int new_value) {
    int* new_array = new int(this->num_element + 1);
    for (size_t i=0; i < this->num_element; i++)
        new_array[i] = this->elements[i];
    delete []this->elements;
    this->elements = new_array;
    this->elements[this->num_element]=new_value;
    this->num_element++;
}

void growing_array::operator=(growing_array const& other) {
    if (this->num_element == other.num_element) {
        delete []this->elements;
        this->elements = new int(other.num_element);
    }
    this->num_element = other.num_element;
    for (size_t i=0; i < other.num_element; i++)
        this->elements[i] = other.elements[i];
}