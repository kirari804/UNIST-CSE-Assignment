 #ifndef STUDENT_MAP_H
#define STUDENT_MAP_H

class StudentMap { // do not change this line
public:
    struct Node // do not change this line
    {
        int student_id; // do not change this line
        int score; // do not change this line
        Node* next;
        /* add whatever you want */
    };

    static const int TABLE_SIZE = 1000; // do not change this line
    Node* table[TABLE_SIZE];


    StudentMap();

    void add_student(int student_id, int score); // do not change this line


    void update_score(int student_id, int new_score); // do not change this line


    int get_score(int student_id) const; // do not change this line


    void remove_student(int student_id);  // do not change this line

    ~StudentMap();


private:
    int hash(int student_id) const; 
};


#endif