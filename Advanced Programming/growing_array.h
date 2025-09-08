#ifndef GROWING_ARRAY_H
#define GROWING_ARRAY_H
using namespace std;
#include <cstddef>

class growing_array {
    int* elements;
    size_t num_element;
public:
    growing_array(); 
    growing_array(growing_array const&);
    ~growing_array(){ delete []this->elements;}
    void append(int);
    void operator=(growing_array const&);
    friend std::ostream& operator<<(std::ostream&, growing_array const&);
};

ostream& operator<<(ostream& out, growing_array const& xs) {
    out <<"[";
    for (size_t i=0; i < xs.num_element; i++) {
        out << xs.elements[i];
        if(i != xs.num_element-1)
            out << ",";
    out << "]";
    }
    return 
}

#endif