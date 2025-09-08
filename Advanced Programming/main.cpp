#include <iostream>
#include "parse.h"
#include "expr.h"
using namespace std;

// int main () {
//     concat a(new bold(new plain("hello")), new plain("there"));
//     a.print(cout);
//     cout << endl;
//     return 0;
// }

int main() {
    cout<<"Expression" << flush;
    expr* e = parse(cin);
    cout << *e << endl;
    delete e;
    return 0;
}