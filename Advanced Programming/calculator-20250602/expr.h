#ifndef EXPR_H
#define EXPR_H

#include <iostream>
#include <cmath>	// for pow()

class expr {
public:
	virtual ~expr() {}
	virtual double evaluate(double) const = 0;
	virtual expr* derivative() const = 0;
	virtual void print(std::ostream&) const = 0;
	virtual expr* copy() const = 0;
	virtual expr* simplify() const { return this->copy(); }

	/*
	 * These two methods are conservative.
	 * If they return true, they are returning the correct answer.
	 * If they return false, they may be returning the correct answer,
	 * or the correct answer may not be known.
	 */
	virtual bool is_zero() const { return false; }
	virtual bool is_one() const { return false; }

	/*
	 * 0 is for 'atoms' (int literals, monomials)
	 * 1 is for multiplication/division
	 * 2 is for addition
	 */
	virtual int precedence() const { return 0; }
};

class int_literal : public expr {
	long value;
public:
	int_literal(long v) : value(v) {}
	double evaluate(double) const override { return this->value; }
	expr* derivative() const override { return new int_literal(0); }
	void print(std::ostream& out) const override { out << this->value; }
	expr* copy() const override { return new int_literal(this->value); }
	bool is_zero() const override { return this->value == 0; }
	bool is_one() const override { return this->value == 1; }
};

class monomial : public expr {
	long power;
public:
	monomial(long power) : power(power) {}
	double evaluate(double x) const override { return pow(x, this->power); }
	expr* derivative() const override;
	void print(std::ostream& out) const override;
	expr* copy() const override { return new monomial(this->power); }
};

class binary_op : public expr {
protected:
	expr* op1, * op2;
	binary_op(expr* op1, expr* op2) : op1(op1), op2(op2) {}
public:
	~binary_op() { delete this->op1; delete this->op2; }
	void print(std::ostream& out) const override;
	virtual char operator_symbol() const = 0;
};

class addition : public binary_op {
public:
	addition(expr* op1, expr* op2) : binary_op(op1, op2) {}
	addition(addition const &);
	void operator=(addition const &);
	char operator_symbol() const override { return '+'; }
	double evaluate(double x) const override;
	expr* derivative() const override;
	expr* copy() const override;
	expr* simplify() const override;
	bool is_zero() const override;
	bool is_one() const override;
	int precedence() const override { return 2; }
};

class multiplication : public binary_op {
public:
	multiplication(expr* op1, expr* op2) : binary_op(op1, op2) {}
	multiplication(multiplication const &);
	void operator=(multiplication const &);
	char operator_symbol() const override { return '*'; }
	double evaluate(double x) const override;
	expr* derivative() const override;
	expr* copy() const override;
	expr* simplify() const override;
	bool is_zero() const override;
	bool is_one() const override;
	int precedence() const override { return 1; }
};

class division : public binary_op {
public:
	division(expr* op1, expr* op2) : binary_op(op1, op2) {}
	char operator_symbol() const override { return '/'; }
	double evaluate(double x) const override;
	expr* derivative() const override;
	expr* copy() const override { return new division(this->op1->copy(), this->op2->copy()); }
	expr* simplify() const override;
	bool is_zero() const override;
	bool is_one() const override;
	int precedence() const override { return 1; }
};

std::ostream& operator<<(std::ostream& out, expr const& e);

#endif
