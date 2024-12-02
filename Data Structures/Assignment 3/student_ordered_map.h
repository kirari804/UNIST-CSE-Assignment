#ifndef STUDENT_ORDERED_MAP_H
#define STUDENT_ORDERED_MAP_H
#include <vector>
#include <climits>
using namespace std;

class StudentOrderedMap { // do not change this line
public:
    struct Node { // do not change this line
        int student_id; // do not change this line
        int score; // do not change this line
        vector<Node*> scanForward;
        Node(int student_id, int score,int lv);
    };
    

    StudentOrderedMap();
    
    void add_student(int student_id, int score);  // do not change this line


    void update_score(int student_id, int new_score); // do not change this line


    int get_student(int score) const; // do not change this line


    void remove_student(int student_id); // do not change this line


    ~StudentOrderedMap();


    /* add whatever you want*/

public:
    Node* head;
    Node* tail;    
    int maxLv;  
    int coin_flip() const;
};

#endif