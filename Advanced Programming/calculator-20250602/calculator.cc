#include "parse.h"
#include <iostream>

using namespace std;

int main() {
	cout << "Expression: " << flush;
	expr* e = parse(cin);
	cout << *e << endl;
	expr* de = e->derivative();
	expr* de_simpl = de->simplify();
	cout << "Derivative: " << *de << endl;
	cout << "Simplified: " << *de_simpl << endl;
	cout << "At x=0: " << e->evaluate(0) << endl;
	cout << "Derivative at x=0: " << de->evaluate(0) << endl;
	delete e;
	delete de;
	delete de_simpl;
	return 0;
}
