#include "doubly_linked_list.h"
#include "container_exception.h"
#include <iostream>
#include <string>
using namespace std;

DoublyLinkedList :: DoublyLinkedList () {
    header = new Node();  
    trailer = new Node();
    header->next = trailer;
    trailer->prev = header;
}
DoublyLinkedList :: ~DoublyLinkedList () {
    while (!empty()) remove_front();
    delete header;
    delete trailer;
}

bool DoublyLinkedList::empty() const {
    if (header->next == trailer) {
        return true;
    }
    return false;
}
    
const std::string& DoublyLinkedList::front() const  {
    if (empty()) {
        throw ContainerEmpty("Container is empty");
    }
    return header->next->ele;
}

const std::string& DoublyLinkedList::back() const {
    if (empty()) {
        throw ContainerEmpty("Container is empty");
    }
    return trailer->prev->ele;
}

void DoublyLinkedList::add_front(const std::string& e) {
    Node* n = new Node;
    n->ele = e;
    n->prev = header;
    n->next = header->next;
    header->next = n;
    if(n->next!=nullptr) {
        n->next->prev = n;
    }
}

void DoublyLinkedList::add_back(const std::string& e) {
    Node* n = new Node;
    n->ele = e;
    n->next = trailer;
    n->prev = trailer->prev;
    trailer->prev = n;
    if(n->prev != nullptr) {
        n->prev->next = n;
    }
    else {
        header->next = n;
    }
}

void DoublyLinkedList::remove_front() {
    if (empty()) {
        throw ContainerEmpty("Container is empty");
    }
    Node* removeNode = header ->next;
    header->next = removeNode->next;
    if (header->next != trailer) {
        header->next->prev = header;
    }
    else {
        trailer->prev = header;
    }
    delete removeNode;
}

void DoublyLinkedList::remove_back() {
    if (empty()) {
        throw ContainerEmpty("Container is empty");
    }
    Node* removeNode = trailer->prev;
    trailer->prev = removeNode->prev;
    if(trailer->prev != header) {
        trailer->prev->next = trailer;
    }
    else {
        header->next = trailer;
    }
    delete removeNode;
}

int DoublyLinkedList::size() const {
    int c = 0;
    Node* cur = header->next;
    while(cur!= trailer) {
        c+=1;
        cur = cur->next;
    
    return c;
}
}