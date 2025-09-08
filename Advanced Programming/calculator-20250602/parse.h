#ifndef PARSE_H
#define PARSE_H

#include "expr.h"
#include <iostream>

/*
 * E.g., parse(std::cin) will construct (on the heap) and return a pointer to an expression tree
 */
expr *parse(std::istream &);

#endif
