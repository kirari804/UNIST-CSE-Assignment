/*
 * You are not expected to read or understand any of this.
 *
 * If you are getting any errors (either compile errors or run-time errors) from this file,
 * it is PROBABLY nothing to do with the code in here. Either you have named a class wrong,
 * don't have your constructors set up the way this file expects, or have screwed up your class
 * in some other way.
 *
 * If you think this file really does have a bug in it, though, let me know!
 *
 * If you are eager and want to read this file anyway....
 * Note that this is not how parsing is typically done. There are two more typical approaches
 * to parsing:
 * 1. Using metaprogramming, we use tools like flex and bison or ANTLR to generate a lexer and
 * a context-free grammar parser.
 * 2. Using parsing combinators, such as Boost.Spirit or Lexy
 *
 * I have chosen to not use either conventional approach because I didn't want to rely on
 * any 3rd-party tool or risk the chance of the code not compiling. Some of you have very unique
 * development environments, so writing everything by hand in basic C++ is the safest option.
 *
 * This is a hand-written recursive-descent parser, where I have used iteration (loops) instead
 * of recursion for some simple right-recursive rules.
 *
 */

#include "parse.h"
#include <optional>
#include <cstdlib>
#include <cctype>
#include <cassert>

using namespace std;

static void skip_whitespace(char const *&inp) {
	for (; *inp && isspace(*inp); inp++);
}

static optional<expr *> parse_expr(char const *&);

static optional<expr *> parse_expr2(char const *&inp) {
	skip_whitespace(inp);
	expr *first_operand;
	if (*inp == '(') {
		inp++;
		first_operand = *parse_expr(inp);
		skip_whitespace(inp);
		assert(*inp == ')');
		inp++;
	} else {
		bool found_parse = false;
		long coeff = 1;
		if (*inp != 'x') {
			assert(isdigit(*inp) || *inp == '-');
			found_parse = true;
			char *end;
			coeff = strtol(inp, &end, 10);
			assert(inp != end);
			inp = end;
			skip_whitespace(inp);
		}
		if (*inp == 'x') {
			found_parse = true;
			inp++;
			long exponent = 1;
			if (*inp != '+') {
				char *end;
				exponent = strtol(inp, &end, 10);
				if (inp == end)
					exponent = 1;
				inp = end;
			}
			first_operand = new monomial(exponent);
			if (coeff != 1)
				first_operand = new multiplication(new int_literal(coeff), first_operand);
		} else if (found_parse)
			first_operand = new int_literal(coeff);
		if (!found_parse)
			return {};
	}
	skip_whitespace(inp);
	char const op = *inp;
	if (op == '*' || op == '/') {
		inp++;
		optional<expr *> second_operand = parse_expr2(inp);
		assert(second_operand.has_value());
		skip_whitespace(inp);
		switch (op) {
		default:	abort();
		case '*':	return new multiplication(first_operand, *second_operand);
		case '/':	return new division(first_operand, *second_operand);
		}
	} else
		return first_operand;	// there was no operation
}

static optional<expr *> parse_expr(char const *&inp) {
	optional<expr *> first_operand = parse_expr2(inp);
	if (!first_operand.has_value())	return {};
	skip_whitespace(inp);
	switch (*inp) {
	default:	return *first_operand;
	case '+': {
		inp++;
		optional<expr *> second_operand = parse_expr(inp);
		if (second_operand.has_value())
			return new addition(*first_operand, *second_operand);
		else
			return first_operand; }
	}
}

expr *parse(istream &in) {
	string ln;
	getline(in, ln);
	char const *s = ln.c_str();
	return *parse_expr(s);
}
