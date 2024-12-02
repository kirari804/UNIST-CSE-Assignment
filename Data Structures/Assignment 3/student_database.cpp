#include "student_database.h"
#include <vector>
#include <stdexcept>
#include "student_ordered_map.h"
#include <set>
using namespace std;

StudentDatabase::StudentDatabase() : map(), ordered_map() {}

void StudentDatabase::add_student(int student_id, int score) {
    map.add_student(student_id, score);
    ordered_map.add_student(student_id, score);
}

void StudentDatabase::update_score(int student_id, int new_score) {
    map.update_score(student_id, new_score);
    ordered_map.update_score(student_id, new_score);
}

int StudentDatabase::get_score(int student_id) const {
    return map.get_score(student_id);
}
int StudentDatabase::get_student(int score) const {
    return ordered_map.get_student(score);
}

void StudentDatabase::remove_student(int student_id) {
    map.remove_student(student_id);
    ordered_map.remove_student(student_id);
}

int** StudentDatabase::get_top_k_students(int k) {
    int** top_k = new int*[k];
    for (int i = 0; i < k; i++) {
        top_k[i] = new int[2]; 
    }
    auto n =  ordered_map.head ->scanForward[0];
    vector<std::pair<int, int>> std;
    while(n!=nullptr) {
        std.push_back({n->student_id, n->score});
        n=n->scanForward[0];
    }
    for (int i = 0; i < k; i++) {
        int max_index = -1;
        int max_score = INT_MIN;
        int max_id = INT_MAX;

        for (int j = 0; j < std.size(); j++) {
            if (std[j].second > max_score || 
                (std[j].second == max_score && std[j].first < max_id)) {
                max_score = std[j].second;
                max_id = std[j].first;
                max_index = j;
            }
        }
        if (max_index != -1) {
            top_k[i][0] = std[max_index].first;  
            top_k[i][1] = std[max_index].second;
            std.erase(std.begin() + max_index); 
        } else {
            top_k[i][0] = -1;
            top_k[i][1] = -1;
        }
    }
    return top_k;
}

int StudentDatabase::get_rank(int score) const {

    set<int> score_list;
    auto n = ordered_map.head->scanForward[0];
    while (n) {
        score_list.insert(n->score);
        n = n->scanForward[0];
    }

    int rank = 1;
    for (auto i = score_list.rbegin(); i != score_list.rend(); i++) {
        if (*i == score) {
            return rank; 
        }
        rank++;
    }

    throw std::runtime_error("Score not found");

}




