#include <iostream>
#include "graph.h"
#include "heap.h"
#include "dijkstra.h"

int main() {
    // Task 1: Test Graph Implementation
    std::cout << "Testing Graph Implementation:\n";
    Graph graph;
    graph.insert_vertex("MomsTouch");
    graph.insert_vertex("KimbapHeaven");
    graph.insert_vertex("Dorm");
    graph.insert_edge("MomsTouch", "KimbapHeaven", 5);
    graph.insert_edge("KimbapHeaven", "Dorm", 3);
    graph.insert_edge("MomsTouch", "Dorm", 10);
    graph.print_graph();

    std::cout << "\nIs MomsTouch adjacent to KimbapHeaven? " << (graph.is_adjacent_to("MomsTouch", "KimbapHeaven") ? "Yes" : "No") << "\n";
    graph.erase_edge("MomsTouch", "KimbapHeaven");
    std::cout << "\nGraph after erasing edge between MomsTouch and KimbapHeaven:\n";
    graph.print_graph();

    // Task 2: Test Heap Implementation
    std::cout << "\nTesting Heap Implementation:\n";
    Heap heap(15); // Heap with capacity 15
    heap.insert(10, "Value10");
    heap.insert(20, "Value20");
    heap.insert(5, "Value5");
    heap.insert(4, "Value4");
    heap.insert(15, "Value15");

    heap.print_heap();

    heap.remove_min();
    std::cout << "\nHeap after removing min:\n";
    heap.print_heap();

    heap.replace_key(2, 3); // Replace key at index 2 with 3
    std::cout << "\nHeap after replacing key at index 2 with 3:\n";
    heap.print_heap();


    // Task 3: Test Dijkstra's algorithm
    std::cout << "\nTesting Dijkstra's algorithm:\n";
    Graph graph2;
    graph2.insert_edge("MomsTouch", "KimbapHeaven", 2);
    graph2.insert_edge("MomsTouch", "Dorm", 5);
    graph2.insert_edge("KimbapHeaven", "Dorm", 1);
    graph2.insert_edge("KimbapHeaven", "GamakLake", 2);
    graph2.insert_edge("Dorm", "GamakLake", 3);
    graph2.insert_edge("Dorm", "Library", 1);
    graph2.insert_edge("GamakLake", "Library", 2);

    Dijkstra dijkstra(&graph2);
    // While you are at MomsTouch, you discover that the cat is in the library!
    std::cout << "Fastest path from MomsTouch to Library:\n";
    dijkstra.get_fastest_path("MomsTouch", "Library");
    std::cout << "Fastest distance from MomsTouch to Library:\n";
    dijkstra.get_fastest_distance("MomsTouch", "Library");

    return 0;
}
