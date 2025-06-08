#include <bits/stdc++.h>
#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <cmath>
#include <limits>
#include <string>
#include <algorithm>
#include <string>

using namespace std;
struct City {
    int id;
    double x, y;
};

double euclideanDistance(const City& a, const City& b) {
    double dx = a.x - b.x;
    double dy = a.y - b.y;
    return std::sqrt(dx * dx + dy * dy);
}


std::vector<int> greedyTour(const std::vector<City>& cities, int start_index) {
    int n = cities.size();
    std::vector<bool> visited(n, false);
    std::vector<int> tour;
    int current = start_index;
    tour.push_back(current);
    visited[current] = true;

    for (int step = 1; step < n; ++step) {
        double min_dist = std::numeric_limits<double>::max();
        int next_city = -1;
        for (int i = 0; i < n; ++i) {
            if (!visited[i]) {
                double dist = euclideanDistance(cities[current], cities[i]);
                if (dist < min_dist) {
                    min_dist = dist;
                    next_city = i;
                }
            }
        }
        if (next_city != -1) {
            visited[next_city] = true;
            tour.push_back(next_city);
            current = next_city;
        }
    }
    assert(tour.size() == n);
    return tour;
}

double tourLength(const std::vector<City>& cities, const std::vector<int>& tour) {
    double total = 0.0;
    int n = tour.size();
    for (int i = 0; i < n; ++i) {
        const City& from = cities[tour[i]];
        const City& to = cities[tour[(i + 1) % n]];
        total += euclideanDistance(from, to);
    }
    return total;
}

int main(int argc, char* argv[])  {
    if (argc != 2) {
        cerr << "Usage: " << argv[0] << " <input_file.tsp>\n";
        return 1;
    }

    string filename = argv[1];
    ifstream infile(filename);
    if (!infile) {
        cerr << "Failed to open file: " << filename << "\n";
        return 1;
    }
    string line;
    size_t dimension = 0;
    // vector<City> cities{dimension};

    // Parse header to find DIMENSION and NODE_COORD_SECTION
    while (getline(infile, line)) {
        if (line.find("DIMENSION") != string::npos) {
            size_t pos = line.find(":");
            if (pos != string::npos) {
                dimension = stoi(line.substr(pos + 1));
            }
        } else if (line.find("NODE_COORD_SECTION") != string::npos) {
            break;
        }
    }
    vector<City> cities;

    // Read city coordinates
    for (size_t i = 0; i < dimension && getline(infile, line); ++i) {
        istringstream iss(line);
        City city;
        iss >> city.id >> city.x >> city.y;
        cities.push_back(city);
    }
    if (cities.empty()) {
        std::cerr << "No cities found in the file." << std::endl;
        return 1;
    }

    double best_length = std::numeric_limits<double>::max();
    std::vector<int> best_tour;

    for (size_t i = 0; i < cities.size(); ++i) {
        std::vector<int> tour = greedyTour(cities, i);
        double length = tourLength(cities, tour);
        if (length < best_length) {
            best_length = length;
            best_tour = tour;
        }
    }

    std::cout << "Best tour length: " << best_length << std::endl;
}

    