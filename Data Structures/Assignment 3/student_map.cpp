#include "student_map.h"
#include <stdexcept>
using namespace std;

StudentMap::StudentMap() { 
    for (int i = 0; i < TABLE_SIZE; ++i) {
        table[i] = nullptr;
    }
}


int StudentMap::hash(int student_id) const {
    return student_id % TABLE_SIZE;
}

void StudentMap::add_student(int student_id, int score) {
    int i = hash(student_id);
    Node* n = new Node;
    n->student_id = student_id;
    n->score = score;
    n->next = table[i];
    table[i] = n;
}

void StudentMap::update_score(int student_id, int new_score) {
    int i = hash(student_id);
    Node* cur = table[i];
    while(cur!=nullptr) {
        if(cur->student_id == student_id) {
            cur->score= new_score;
            return;
        }
        cur = cur -> next;
    }
    throw std::runtime_error("Student ID not found");
}

int StudentMap::get_score(int student_id) const {
    int i = hash(student_id);
    Node* cur = table[i];
    while (cur!=nullptr) {
        if (cur->student_id == student_id) {
            return cur->score;
        }
        cur = cur->next;
    }
    throw std::runtime_error("Student ID not found");
}

void StudentMap::remove_student(int student_id) {
    int i = hash(student_id);
    Node*n = table[i];
    Node* prev = nullptr;   
    while (n!=nullptr) {
        if(n->student_id==student_id) {
            if (prev!= nullptr) {
                prev->next = n->next;
            }
            else {
                table[i] = n->next;
            }
        delete n;
        return;
        }
    prev = n;
    n= n->next;
    }
    throw std::runtime_error("Student ID not found");
}

StudentMap::~StudentMap(){
    for(int i = 0; i<TABLE_SIZE; i++) {
        Node* cur = table[i];
        while (cur!=nullptr) {
            Node* n = cur;
            cur = cur -> next;
            delete n;
        }
    }
}
