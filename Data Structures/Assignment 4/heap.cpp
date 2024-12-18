#include "heap.h"
 
Heap::Heap(int capacity): capacity(capacity), size(0)
{
    arr = (int*)malloc(sizeof(int)*(capacity+1));
    values_arr = (std::string*)malloc(sizeof(std::string)*(capacity+1));
    if (!arr || !values_arr)
        throw std::bad_alloc();
}

Heap::~Heap() 
{
    free(arr);
    for (unsigned i = 1; i < capacity; ++i)
        values_arr[i].resize(0);
    free(values_arr);
}

bool Heap::empty() const
{
    return (size == 0);
}

void Heap::insert(int key, const std::string& value) 
{
    arr[++size] = key;
    values_arr[size] = value;
    upheap(size);
}

void Heap::remove_min() {
    arr[1] = arr[size];
    values_arr[1] = values_arr[size];
    size = size -1;
    downheap(1);
}

std::pair<int, std::string> Heap::return_min() const {
    return std::make_pair(arr[1], values_arr[1]);
}

void Heap::replace_key(int index, int new_key) {
    arr[index] = new_key;
    if (index > 1 && arr[index] < arr[index/2]) {
        upheap(index);
    }
    else {
        downheap(index);
    }
}

void Heap::print_heap() const {
    if (size==0)
        std::cout << " " << std::endl;
    int node_current_level=0;
    int node_next_level = 1;
    for (int i = 1; i <= size; ++i) {
        std::cout << arr[i] << " ";
        node_current_level ++;
        if(node_current_level == node_next_level){
            std::cout << std::endl;
            node_next_level= node_next_level*2;
            node_current_level = 0;
        }
    }
        if (node_current_level > 0) {
            std::cout << std::endl;
    }
}

