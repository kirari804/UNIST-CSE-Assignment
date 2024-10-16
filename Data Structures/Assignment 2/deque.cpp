/* Write your code here */
#include "deque.h"
#include "stack.h"
#include "container_exception.h"
#include <iostream>
#include <string>
using namespace std;




bool Deque::empty() const {
    return list.empty();
}

int Deque::size() const {
    return list.size();
}

const string& Deque::front() const {
    return list.front();
}

const string& Deque::back() const {
    return list.back();
}

void Deque::push_front(const std::string& e) {
    list.add_front(e);
}

void Deque::push_back(const std::string& e) {
    list.add_back(e);
}

void Deque::pop_front() {
    list.remove_front();
}

void Deque::pop_back() {
    list.remove_back();
}

void Deque::reverse() {
    Stack s;
    while(!list.empty()) {
        s.push(list.front());
        list.remove_front();
    }
    while (!s.empty()) {
        list.add_back(s.top());
        s.pop();
    }
}
