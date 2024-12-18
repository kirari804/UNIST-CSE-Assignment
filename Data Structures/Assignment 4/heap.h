#ifndef HEAP_H
#define HEAP_H

#include <string>
#include <iostream>

// Do not change the class name
class Heap {
private:
    int* arr;
    std::string* values_arr;
    int capacity;
    int size;
    void resize(int new_capa) {
        this->arr = (int*)realloc(this->arr, sizeof(int)*(new_capa+1));
        this->values_arr = (std::string*)realloc(this->values_arr, sizeof(std::string)*(new_capa+1));
        capacity = new_capa;
        if(!this->arr || !values_arr) 
            throw std::bad_alloc();
    }

    int parent(int i) {
        return i/2;
    }

    void upheap(int i) {
        while (i >1) {
            int parent_index = parent(i);
            if (arr[parent_index] > arr[i]) {
                int temp = arr[parent_index];
                arr[parent_index] = arr[i];
                arr[i] = temp;
                values_arr[parent_index].swap(values_arr[i]);
                i = parent_index;
            }
            else 
                break;
        }
    }

    void downheap(int i) {
        int left = 2*i;
        int right = 2*i+1;
        int min = i;
        while(true) {
            if(left <= size && arr[left] < arr[min]) 
                min = left;
            if (right <= size &&arr[right] < arr[min])
                min = right;
            if (i!= min) {
                int temp = arr[i];
                arr[i] = arr[min];
                arr[min] = temp;
                values_arr[i].swap(values_arr[min]);
                i = min;
                left = 2*i;
                right = 2*i+1;
            }
            else
                break;
        }
    }
public:

    // Do not change the declaration of the function below
    Heap(int capacity);

    // Do not change the declaration of the function below
    ~Heap();

    // Do not change the declaration of the function below
    bool empty() const;

    // Do not change the declaration of the function below
    void insert(int key, const std::string& value);

    // Do not change the declaration of the function below
    void remove_min();

    // Do not change the declaration of the function below
    // This assumes that it's a vector-based heap implementation. Here, "index" means the rank in the vector-based heap implementation, and it starts from 1 (root).
    void replace_key(int index, int new_key);

    // Do not change the declaration of the function below
    // This prints the keys in the heap. For each line, print the keys at the same depth, from left to right, separated by a single space (" "). It starts with the root node and proceeds to the deepest nodes, increasing the depth by one for each line.
    void print_heap() const;

    std::pair<int, std::string>  return_min() const;

    /* add whatever you want*/

};

/* add whatever you want*/


#endif // HEAP_H