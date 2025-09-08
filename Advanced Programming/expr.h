#ifndef EXPR_H
#define EXPR_H
#include <iostream>
#include <math.h>
using namespace std;
class expr {
public:
    virtual ~expr() {}
    virtual double evaluate(double) const {return 0;}
    virtual expr* derivative() const {return nullptr;}
    virtual void print(ostream&) const {}
    virtual expr* copy() const {return nullptr; }
};

class int_literal:public expr {
    long value;
public:
    int_literal(long v): value(v) {}
    double evaluate(double) const override {return this->value;}
    expr* derivative() const { return new int_literal(0);}
    void print(ostream& out) const override {out<< this->value;}
    expr* copy() const override { return new int_literal(this->value);}
};

class monomial:public expr {
    long power;
public:
    monomial(long power): power(power) {}
    double evaluate(double x) const override {return pow(x, this->power);}
    expr* derivative() const override;
    void print(ostream& out) const override;
    expr* copy() const override {return new monomial(this->power);}
};

class binary_op:public expr {
protected:
    expr* op1, *op2;
    binary_op(expr* op1, expr* op2): op1(op1), op2(op2) {}
public:
    ~binary_op() {delete this->op1; delete this->op2;}
    void print(ostream& out) const override;
    virtual char operator_symbol() const=0;
};

class multiplication:public binary_op {
public:
    multiplication(expr* op1, expr* op2): binary_op(op1, op2) {}
    multiplication(multiplication const&);
    void operator*(multiplication const&);
    char operator_symbol() const override {return '*';}
    double evaluate(double r) const override;
    expr* derivative() const override;
    expr* copy() const override;
};

class addition:public binary_op {
public:
    addition(expr* op1, expr* op2): binary_op(op1, op2){}
    addition(expr* const &);
    void operator+(addition cosnt&);
    char operator_symbol() const override {return '+';}
    double evaluate(double x) const override;
    expr* derivative() const override;
};

class division:public binary_op {
public:
    division(expr*, expr*): binary_op(nullptr, nullptr) {}
    char operator_symbol() const override {return '/';}
};


#endif