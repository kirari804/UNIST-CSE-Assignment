#include <iostream>
using namespace std;

class fraction {
    long numer, denum;
public:
    fraction(long n, long d=1) //CONSTRUCTOR
        : numer(n), denum(d) { //initialize
        }
    bool operator<=(fraction const& other) {
        //EVERY parameter has an implicit hidden parameters called
        //'this', which is of type fraction
        long this_numer = this->numer * other.denum;
        long other_numer = other.numer*this->denum;
        return this_numer <=  other_numer;
    }
    void operator+=(fraction const& other) {
        long new_numer = this->numer * other.denum + other.numer*this->denum;
        long new_denum = this->denum * other.denum;
        this->numer = new_numer;
        this->denum = new_denum;
    }
    friend ostream& operator<<(ostream&, fraction const&);
};

ostream& operator<<(ostream& out, fraction const& f) {
    return out << f.numer << "/" << f.denum;
}

int main() {
    fraction f(2,3);
    fraction g(5,8);
    fraction h = 2;
    cout << (f<=g) << endl;
    g += fraction(1,5);
    cout << (f<=g) << endl;
    g+=1;
    cout << (g<=h) <<endl;
    return 0;
}
