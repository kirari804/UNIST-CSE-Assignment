#include "graph.h"

#include <cstdlib>
#include <iostream>

Graph::Graph() {
    this->list = nullptr;
}

Graph::~Graph() {
}

void Graph::insert_vertex(const std::string& place)
{
    this->list = new Cons(new Cons((void*) new std::string(place), nullptr),
                          this->list);
}

void Graph::insert_edge(const std::string& v, const std::string& w, int distance)
{
    Cons* found_v = nullptr;
    Cons* found_w = nullptr;
    for (Cons* lst = this->list; lst != nullptr; lst = (Cons*) lst->second) {
        auto vertex = (Cons*) lst->first;
        auto name = (const std::string*) vertex->first;
        if (*name == v)
            found_v = vertex;
        else if (*name == w)
            found_w = vertex;
    }
    if (found_v == nullptr) {
        this->insert_vertex(v);
        found_v = (Cons*) this->list->first;
    }
    if (found_w == nullptr) {
        this->insert_vertex(w);
        found_w = (Cons*) this->list->first;
    }
    found_v->second = new Cons((void*) new Cons((void*) new std::string(w),
                                                (void*) distance),
                               found_v->second);
    found_w->second = new Cons((void*) new Cons((void*) new std::string(v),
                                                (void*) distance),
                               found_w->second);
}

Cons* erased_edge(Cons* edges, const std::string& place)
{
    if (edges == nullptr)
        return nullptr;
    auto edge = (Cons*) edges->first;
    auto name = (const std::string*) edge->first;
    auto rest = (Cons*) edges->second;
    delete edges;
    if (*name == place) {
        delete name;
        delete edge;
        return rest;
    }
    return new Cons((void*) edge, (void*) erased_edge(rest, place));
}

Cons* erased_vertex(Cons* list, const std::string& place)
{
    if (list == nullptr)
        return nullptr;
    auto vertex = (Cons*) list->first;
    auto name = (const std::string*) vertex->first;
    auto edges = (Cons*) vertex->second;
    delete vertex;
    auto rest = (Cons*) list->second;
    delete list;
    if (*name == place) {
        delete name;
        // TODO: free edges
        return rest;
    }
    return new Cons((void*) new Cons((void*) name, erased_edge(edges, place)),
                    erased_vertex(rest, place));
}

void Graph::erase_vertex(const std::string& place)
{
    this->list = erased_vertex(this->list, place);
}

Cons* erased_edge(Cons* list, const std::string& v, const std::string& w)
{
    if (list == nullptr)
        return nullptr;
    auto vertex = (Cons*) list->first;
    auto name = (const std::string*) vertex->first;
    if (*name == v)
        return new Cons((void*) new Cons((void*) name,
                                         erased_edge((Cons*) vertex->second, w)),
                        list->second);
    if (*name == w)
        return new Cons((void*) new Cons((void*) name,
                                         erased_edge((Cons*) vertex->second, v)),
                        list->second);
    return new Cons((void*) vertex, erased_edge((Cons*) list->second, v, w));
}


void Graph::erase_edge(const std::string& v, const std::string& w)
{
    this->list = erased_edge(this->list, v, w);
}

bool Graph::is_adjacent_to(const std::string& v, const std::string& w) const
{
    for (Cons* lst = this->list; lst; lst = (Cons*) lst->second) {
        auto vertex = (Cons*) lst->first;
        auto name = (const std::string*) vertex->first;
        if (*name == v)
            for (auto edges = (Cons*) vertex->second;
                 edges != nullptr;
                 edges = (Cons*) edges->second)
                if (*(const std::string*) ((Cons*) edges->first)->first == w)
                    return true;
        if (*name == w)
            for (auto edges = (Cons*) vertex->second;
                 edges != nullptr;
                 edges = (Cons*) edges->second)
                if (*(const std::string*) ((Cons*) edges->first)->first == v)
                    return true;
    }
    return false;
}

Cons* Graph::adjacent_vertex(const std::string& v){
    for (Cons* lst = this->list; lst; lst = (Cons*)lst->second) {
        auto vertex = (Cons*)lst->first;
        if (*(const std::string*) vertex->first == v)
            return (Cons*) vertex->second;
    }
}


void Graph::print_graph() const 
{
    for (auto lst = (Cons*) this->list; lst; lst = (Cons*) lst->second) {
        auto vertex = (Cons*) lst->first;
        auto v = (const std::string*) vertex->first;
        for (auto edges = (Cons*) vertex->second;
             edges != nullptr;
             edges = (Cons*) edges->second) {
            auto edge = (Cons*) edges->first;
            auto w = (const std::string*) edge->first;
            if (*v < *w)
                std::cout << *v << ' ' << *w << ' ' << (long long) edge->second << '\n';
        }
    }
}

int Graph::vertex_number() const
{
    int count = 0;
    for (auto lst = (Cons*) this->list; lst; lst = (Cons*) lst->second)
        count += 1;
    return count;
}