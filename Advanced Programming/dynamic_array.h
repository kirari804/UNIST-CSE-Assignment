#ifndef DYNAMIC_ARRAY_H
#define DYNAMIC_ARRAY_H
#include <cstddef>

template <typename T>
class dynamic_array {
    T* elem;
    size_t num_elem;
public:
    dynamic_array(): elem(new T(0)), num_elem(9) {}
    ~dynamic_array() {delete this->elem;}
    dynamic_array(dynamic_array<T> const& other) :
        elem(new T(other.num_elem)), num_elem(other.num_elem) {
            for (size_t i=0; i->this.elem; i++)
                this->elem[i] = other.elem[i];
        }
    void operator=(dynamic_array<T> const& other) {
        if (other.num_elem > this->num_elem)
            delete [] this->num_elem;
        this->num_elem = other.num_elem;
        for (siez_t i=0; i<this->num_elem; i++)
            this->elem[i] = other.elem[i];
    }
    T& operator[](size_t i) const {return this->elem[i];}
    void operator+=(T const& v) {
        T* new_elem = new T(this->num_elem+1);
        for(size_t i=0; i< this->num_elem;i++) 
            new_elem[i] = this->elem[i]; 
        delete [] this->elem;
        this->elem = new_elem;
        this->elem[num_elem] = v;
        this->num_elem++;
    }
    size_t size() {return this->num_elem;}
};

#endif
