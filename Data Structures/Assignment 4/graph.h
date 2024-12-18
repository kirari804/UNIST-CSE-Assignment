#ifndef GRAPH_H
#define GRAPH_H

#include <string>

struct Cons {
    void* first;
    void* second;
    Cons(void* first, void* second) : first {first}, second {second} {}
};

// Do not change the class name
class Graph {
public:

    // Do not change the declaration of the function below
    Graph();

    // Do not change the declaration of the function below
    ~Graph();


    // Do not change the declaration of the function below
    void insert_vertex(const std::string& place);

    // Do not change the declaration of the function below
    void insert_edge(const std::string& v, const std::string& w, int distance);

    // Do not change the declaration of the function below
    void erase_vertex(const std::string& place);

    // Do not change the declaration of the function below
    void erase_edge(const std::string& v, const std::string& w);

    // Do not change the declaration of the function below
    bool is_adjacent_to(const std::string& v, const std::string& w) const;

    // Do not change the declaration of the function below
    // This prints the structure of the graph. The format is as follows: for each line, print each edge in the format "node1 node2 weight of the edge," with each element separated by a single space.
    void print_graph() const;

    int vertex_number() const;

    Cons* adjacent_vertex(const std::string& v);

    Cons* list;
    /* add whatever you want*/
};

#endif // GRAPH_H