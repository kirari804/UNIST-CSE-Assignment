/* Write your code here */
#include "stack.h"
#include "container_exception.h"
#include <iostream>
#include <string>
using namespace std;

Stack::Stack(int size) {
    capacity = size;
    top_index = -1;
    data = new string[capacity];
}

Stack::~Stack() {
    delete[] data;
}

bool Stack::empty() const {
    return (top_index==-1);
}

const std::string& Stack::top() const {
    if (empty()) {
        throw ContainerEmpty("Container is empty");
    }
    return data[top_index];
}

void Stack::push(const std::string& e) {
    if(top_index+1 >= capacity) {
        throw ContainerOverflow("Stack is full");
    }
    top_index++;
    data[top_index] = e;
}

void Stack::pop() {
    if (empty()) {
        throw ContainerEmpty("Container is empty");
    }
    top_index--;
}

int Stack::size() const {
    int size = top_index+1;
    return size;
}