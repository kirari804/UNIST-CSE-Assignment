#include <iostream>
#include <fstream>
using namespace std;

struct record {
    int col1;
    double col2;
};

istream& operator>>(istream& in, record& r) {
    in >> r.col1;
    in.ignore(1, '.');
    return in >> r.col2;
}

class plain_text_report : public record{
public:
    plain_text_report(record const* rs, size_t  n): report(rs,n);
    void print_headings() const override {

    }
    void print
}

int main() {
    record rs[100];
    size_t n=0;
    fstream f["a csv"];
    while (true) {
        f >> rs[n];
        if (f)
            n++;
        else
            break;
    }
    return
}