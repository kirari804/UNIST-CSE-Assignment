#include <bits/stdc++.h>
#include <iostream>
using namespace std;


struct City {
    int id;
    double x, y;
};

pair<double, vector<int>> heldKarp(const vector<vector<double>>& dist) {
    int n = dist.size();
    int N = 1 << n;                     // number of subsets
    double inf = std::numeric_limits<double>::infinity();

    // dp[mask][j] = min cost to start at 0, visit exactly the cities in mask, and end at j
    vector<vector<double>> dp(N, vector<double>(n, inf));
    // parent[mask][j] = best predecessor of j in the optimal path for (mask, j)
    vector<vector<int>> parent(N, vector<int>(n, -1));

    dp[1][0] = 0;  // base case: mask=1<<0, at city 0, cost=0

    // Build up DP table
    for (int mask = 1; mask < N; ++mask) {
        if ((mask & 1) == 0) continue;  // we always include city 0 in the tour
        for (int j = 1; j < n; ++j) {
            if ((mask & (1 << j)) == 0) continue;
            int prevMask = mask ^ (1 << j);
            for (int k = 0; k < n; ++k) {
                if (prevMask & (1 << k)) {
                    double cost = dp[prevMask][k] + dist[k][j];
                    
                    if (cost < dp[mask][j]) {
                        dp[mask][j] = cost;
                        parent[mask][j] = k;
                    }
                }
            }
        }
    }

    // Close the tour by returning to city 0
    int fullMask = N - 1;
    double minCost = inf;
    int lastCity = 0;
    for (int j = 1; j < n; ++j) {
        double cost = dp[fullMask][j] + dist[j][0];
        if (cost < minCost) {
            minCost = cost;
            lastCity = j;
        }
    }

    // Reconstruct the optimal tour
    vector<int> tour;
    int mask = fullMask, cur = lastCity;
    while (cur != 0) {
        tour.push_back(cur);
        int p = parent[mask][cur];
        assert(p>=0);
        mask ^= (1 << cur);
        cur = p;
    }
    tour.push_back(0);           // add the start city
    reverse(tour.begin(), tour.end());
    tour.push_back(0);           // return to start

    return {minCost, tour};
}

int main(int argc, char* argv[]) {

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

    for (size_t i = 0; i < dimension && getline(infile, line); ++i) {
        istringstream iss(line);
        City city;
        iss >> city.id >> city.x >> city.y;
        cities.push_back(city);
    }

    // Build Euclidean distance matrix
    int n = cities.size();
    vector<vector<double>> dist;
    for (size_t i = 0; i < n; ++i) {
        dist.push_back({});
        for (size_t j = 0; j < n; ++j) {
            if (i == j) {
                dist[i].push_back(0);
            } else {
                double dx = cities[i].x - cities[j].x;
                double dy = cities[i].y - cities[j].y;
                dist[i].push_back(sqrt(dx * dx + dy * dy));
            }

        }
    }
    


    // Solve TSP using Held-Karp algorithm
    auto [cost, tour] = heldKarp(dist);

    // Output the results
    // cout << "File: " << filename << "\n";
    cout << "Minimum tour cost: " << cost << "\n";
    cout << "Tour: ";
    for (int v : tour) {
        cout << v << " ";
    }
    cout << "\n";

    return 0;
}