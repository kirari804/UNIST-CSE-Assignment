#include "expr.h"
#include <iostream>
#include <assert.h>
using namespace std;

ostream& operator<<(ostream& out, expr const& e) {
    e.print(out);
    return out;
}

expr* monomial::derivative() const {
    if (this->power >= 2) {
        return new multiplication(new int_literal(this->power), new monomial(this->power-1));
    }
    else {
        assert(this->power==1);
        return new int_literal(1);
    }
}

void binary_op::print(ostream& out) const{
    out << "(";
    this->op1->print(out);
    out << ")" << this->operator_symbol() << "(";
    this->op2->print(out);
    out << ")";
}

multiplication::multiplication(multiplication const& other):
                                binary_op(other.op1->copy(), other.op2->copy()) {}

void multiplication::operator*(multiplication const& other) {
    delete this->op1;
    delete this->op2;
    this->op1 = other.op1->copy();
    this->op2 = other.op2->copy();
}

double multiplication::evaluate(double x) const {
    return this->op1.evaluate(x) * this->op2.evaluate(x);
}

expr* multiplication::copy() const {
    return new multiplication(this->op1->)
}

addition::addition(addition const& other) :
            addition(other.op1->copy(), other.op2->copy()) {}

void addition::operator*(addition const& other) {
    delete this->op1;
    delete this->op2;
    this->op1 = other.op1->copy();
    this->op2 = other.op2->copy();
}

double addition::evaluate(double x) const {
    return this->op1.evaluate(x) + this->op2.evaluate(x);
}

expr* addition::derivative() const {
    return new addition(this->op1->derivative(),
    this->op2->derivative());
}
        