#include "student_ordered_map.h"
#include <climits>
#include <cstdlib>
#include <stdexcept>
using namespace std;

StudentOrderedMap::Node::Node(int student_id, int score,int lv) {
            this->student_id = student_id;
            this->score= score;
            scanForward = vector<Node*>(lv+1, nullptr);
        }
        
StudentOrderedMap::StudentOrderedMap() : maxLv {0} {
    head = new Node(INT_MIN, 0 , maxLv);
    tail = new Node(INT_MAX, 0 , maxLv);
    for (int i = 0; i<maxLv; i++) {
        head->scanForward[i] = tail;
    }
}

int StudentOrderedMap::coin_flip() const {
    int lv = 1;
    while(rand() < RAND_MAX /2 && lv < maxLv) {
        lv++;
    }
    return lv;
}

void StudentOrderedMap::add_student(int student_id, int score) {
    vector<Node*> update(maxLv, head);
    Node*n = head;
 
    for (int i = maxLv -1; i>=0; i--) {
        while (n->scanForward[i] && n->scanForward[i]->score < score) {
            n=n->scanForward[i];
        }
        update[i] = n;
    }

    int lv = coin_flip();
    if(lv>maxLv) {
        update.resize(lv + 1, head);
        for (int i = maxLv+1; i <= lv; i++) {
            update[i] = head;
        }
        maxLv = lv;
    }
    Node* x = new Node(student_id, score, lv);
    for (int i = 0; i <= lv; i++) {
        if (update[i]) {
            x-> scanForward[i] = update[i] -> scanForward[i];
            update[i]->scanForward[i]= x;
        }
    }
}

void StudentOrderedMap::update_score(int student_id, int new_score) {
    Node* cur = head->scanForward[0];
    Node* n = head;
    Node* result = nullptr;
    while (cur) {
        if(cur->student_id==student_id) {
            result = cur;
            break;
        }
        n=cur;
        cur=cur->scanForward[0];
    }
    if(!result) {
        throw std::runtime_error("Student ID not found");
    }
    for(int i = 0; i<=maxLv;i++) {
        if (n->scanForward[i]!=result) {
            break;
        }
        n->scanForward[i]= cur->scanForward[i];
    }
    delete result;
    add_student(student_id, new_score);
}

int StudentOrderedMap::get_student(int score) const {
    Node* x = head;
    for (int i = maxLv-1; i>=0; i--) {
        while (x->scanForward[i] && x->scanForward[i]->score < score) {
            x = x->scanForward[i];
        }
    }
    x = x->scanForward[0];
    int id = INT_MAX;
    while (x != nullptr) {
        if (x->score == score){
            if (x->student_id < id) {
                id = x->student_id;
            }
        }
        x = x->scanForward[0];
    }
    if (id != INT_MAX) {
        return id;
    }
    throw std::runtime_error("Score not found");
}

void StudentOrderedMap::remove_student(int student_id) {
    Node* cur = head->scanForward[0];
    Node* n = head;
    Node* result = nullptr;
    while (cur) {
        if(cur->student_id==student_id) {
            result = cur;
            break;
        }
        n=cur;
        cur=cur->scanForward[0];
    }
    if(!result) {
        throw std::runtime_error("Student ID not found");
    }
    for(int i = 0; i<=maxLv;i++) {
        if (n->scanForward[i]!=result) {
            break;
        }
        n->scanForward[i]= cur->scanForward[i];
    }
    delete result;
    while (maxLv > 0 && head->scanForward[maxLv] == nullptr) {
        maxLv--;
    }
}

StudentOrderedMap::~StudentOrderedMap() {
    Node* cur = head;
    while (cur != nullptr) {
        Node* next = cur->scanForward[0]; 
        delete cur;
        cur = next;
    }
}