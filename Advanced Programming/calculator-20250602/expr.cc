#include "expr.h"
#include <cassert>

using namespace std;

std::ostream& operator<<(std::ostream& out, expr const& e) {
	e.print(out);
	return out;
}



expr* monomial::derivative() const {
	if (this->power >= 2)
		return new multiplication(
			new int_literal(this->power),
			new monomial(this->power - 1)
		);
	else {
		assert(this->power == 1);
		return new int_literal(1);
	}
}
void monomial::print(ostream& out) const {
	if (this->power == 1)	out << "x";
	else					out << "x" << this->power;
}



void binary_op::print(ostream& out) const {
	if (this->op1->precedence() > this->precedence())
		out << "(";
	this->op1->print(out);
	if (this->op1->precedence() > this->precedence())
		out << ")";
	cout << " " << this->operator_symbol() << " ";
	if (this->op2->precedence() > this->precedence())
		out << "(";
	this->op2->print(out);
	if (this->op2->precedence() > this->precedence())
		out << ")";
}



multiplication::multiplication(multiplication const& other)
	: binary_op(other.op1->copy(), other.op2->copy()) {}
void multiplication::operator=(multiplication const& other) {
	delete this->op1;
	delete this->op2;
	this->op1 = other.op1->copy();
	this->op2 = other.op2->copy();
}
double multiplication::evaluate(double x) const {
	return this->op1->evaluate(x) * this->op2->evaluate(x);
}
expr* multiplication::derivative() const {
	return new addition(
		new multiplication(
			this->op1->copy(), this->op2->derivative()
		), new multiplication(
			this->op1->derivative(), this->op2->copy()
		)
	);
}
expr* multiplication::copy() const {
	return new multiplication(this->op1->copy(), this->op2->copy());
}
expr* multiplication::simplify() const {
	if (this->op1->is_zero() || this->op2->is_zero())
		return new int_literal(0);
	if (this->op1->is_one())
		return this->op2->simplify();
	if (this->op2->is_one())
		return this->op1->simplify();
	return new multiplication(this->op1->simplify(), this->op2->simplify());
}
bool multiplication::is_zero() const {
	return this->op1->is_zero() || this->op2->is_zero();
}
bool multiplication::is_one() const {
	return this->op1->is_one() && this->op2->is_one();
}




addition::addition(addition const& other)
	: addition(other.op1->copy(), other.op2->copy()) {
}
void addition::operator=(addition const& other) {
	delete this->op1;
	delete this->op2;
	this->op1 = other.op1->copy();
	this->op2 = other.op2->copy();
}
double addition::evaluate(double x) const {
	return this->op1->evaluate(x) + this->op2->evaluate(x);
}
expr* addition::derivative() const {
	return new addition(
		this->op1->derivative(),
		this->op2->derivative()
	);
}
expr* addition::copy() const {
	return new addition(this->op1->copy(), this->op2->copy());
}
expr* addition::simplify() const {
	if (this->op1->is_zero())
		return this->op2->simplify();
	if (this->op2->is_zero())
		return this->op1->simplify();
	return new addition(this->op1->simplify(), this->op2->simplify());
}
bool addition::is_zero() const {
	return this->op1->is_zero() && this->op2->is_zero();
}
bool addition::is_one() const {
	return (this->op1->is_zero() && this->op2->is_one())
	|| (this->op1->is_one() && this->op2->is_zero());
}



double division::evaluate(double x) const {
	return this->op1->evaluate(x) / this->op2->evaluate(x);
}
#define PLUS(a, b)	(new addition(a, b))
#define NEG(a)	(new multiplication(new int_literal(-1), a))
#define MINUS(a, b)	PLUS(a, NEG(b))
#define TIMES(a, b)	(new multiplication(a, b))
#define DIV(a, b)	(new division(a, b))
expr* division::derivative() const {
	return DIV(MINUS(TIMES(op1->copy(), op2->derivative()),
			TIMES(op1->derivative(), op2->copy())),
			TIMES(op2->copy(), op2->copy()));
}
bool division::is_zero() const {
	return this->op1->is_zero();
}
bool division::is_one() const {
	return this->op1->is_one() && this->op2->is_one();
}
expr* division::simplify() const {
	if (this->op1->is_zero())
		return new int_literal(0);
	if (this->op2->is_one())
		return this->op1->simplify();
	return new division(this->op1->simplify(), this->op2->simplify());
}
