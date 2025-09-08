#include <iostream>
#include <cmath>

double  distance(double x1, double y1, double x2, double y2) {
    double x_diff = x1-x2;
    double y_diff = y1-y2;
    return sqrt((x_diff)*(x_diff) + (y_diff)*(y_diff));
}

int main() {
    using namespace std;
    double prev_x, prev_y;
    bool is_run = false;
    double total = 0;
    while (true) {
        double x,y ;
        cout << "Enter x,y: " << flush;
        cin >> x >> y;
        if (!cin)
            break;
        if (is_run)
            total += distance(prev_x, x, prev_y, y);
        prev_x = x;
        prev_y = y;
        is_run =true;
    }
    cout << total;
    return 0;
}