#include "dijkstra.h"
#include <iostream>

constexpr int INF = ((unsigned) -1) >> 1; 

Dijkstra::Dijkstra(Graph* graph) : graph(graph) {

}

int vertex_index(const std::string& v,
    const std::string* vertex, int v_count)
{
    for (int i = 0; i < v_count; ++i)
        if (vertex[i] == v)
            return i;
    return -1; 
}

void Dijkstra::get_fastest_path(const std::string& source, const std::string& destination) {
    int v_count = graph->vertex_number();
    auto vertex = new std::string[v_count];
    {
        int i = 0;
        for (auto lst = (Cons*) this->graph->list; lst; lst = (Cons*) lst->second, ++i) {
            auto v = (Cons*) lst->first;
            vertex[i] = *(const std::string*) v->first;
        }
    }
    auto shortest_dist = new int[v_count];
    auto next = new int[v_count];
    for (int i = 0; i < v_count; ++i)
        shortest_dist[i] = INF;
    Heap q(v_count);
    int source_index = vertex_index(source, vertex, v_count);
    int dest_index = vertex_index(destination, vertex, v_count);
    shortest_dist[source_index] = 0;
    q.insert(0, source);
    while (!q.empty()) {
        const auto [distance, current_vertex] = q.return_min();
        const int index = vertex_index(current_vertex, vertex, v_count);
        q.remove_min();
        if (index == dest_index) {
            std::cout << source;
            for (int i = source_index;
                 i != dest_index;
                 std::cout << ' ' << vertex[i = next[i]]);
            std::cout << std::endl;
            return;
        }

        Cons* neighbors = graph->adjacent_vertex(vertex[index]);
        for (Cons* neighbor = neighbors;
             neighbor;
             neighbor = (Cons*)neighbor->second) {
            auto* neighbor_data = (Cons*)neighbor->first;

            auto* neighbor_vertex = (std::string*) neighbor_data->first; 
            int neighbor_vertex_index = vertex_index(*neighbor_vertex, vertex, v_count);
            int weight = (long long) neighbor_data->second;      
        
            int new_dist = distance + weight;
            if (new_dist < shortest_dist[neighbor_vertex_index]) {
                shortest_dist[neighbor_vertex_index] = new_dist;
                next[index] = neighbor_vertex_index;
                q.insert(new_dist, *neighbor_vertex);
            }
        }
    }
}

void Dijkstra::get_fastest_distance(const std::string& source, const std::string& destination)
{
    int v_count = graph->vertex_number();
    auto vertex = new std::string[v_count];
    {
        int i = 0;
        for (auto lst = (Cons*) this->graph->list; lst; lst = (Cons*) lst->second, ++i) {
            auto v = (Cons*) lst->first;
            vertex[i] = *(const std::string*) v->first;
        }
    }
    auto shortest_dist = new int[v_count];
    for (int i = 0; i < v_count; ++i)
        shortest_dist[i] = INF;
    Heap q(v_count);
    int source_index = vertex_index(source, vertex, v_count);
    int dest_index = vertex_index(destination, vertex, v_count);
    shortest_dist[source_index] = 0;
    q.insert(0, source);
    while (!q.empty()) {
        const auto [distance, current_vertex] = q.return_min();
        const int index = vertex_index(current_vertex, vertex, v_count);
        q.remove_min();
        if (index == dest_index) {
            std::cout << shortest_dist[index] << std::endl;
            return;
        }

        Cons* neighbors = graph->adjacent_vertex(vertex[index]);
        for (Cons* neighbor = neighbors;
             neighbor;
             neighbor = (Cons*)neighbor->second) {
            auto* neighbor_data = (Cons*)neighbor->first;

            auto* neighbor_vertex = (std::string*) neighbor_data->first; 
            int neighbor_vertex_index = vertex_index(*neighbor_vertex, vertex, v_count);
            int weight = (long long) neighbor_data->second;      
        
            int new_dist = distance + weight;
            if (new_dist < shortest_dist[neighbor_vertex_index]) {
                shortest_dist[neighbor_vertex_index] = new_dist;
                q.insert(new_dist, *neighbor_vertex);
            }
        }
    }
}
