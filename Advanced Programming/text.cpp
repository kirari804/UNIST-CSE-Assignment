#include <iostream>
#include "text.h"
using namespace std;

void concat::print(ostream& out, string attr) const {
    this->left->print(out, attr);
    out << "\e[0n";
    this->right->print(out, attr);
}

void bold::print(ostream& out, string attr) const {
    this->child->print(out, attr + "\e[1n");
}

static int ansi_color_code(color c) {
    switch (c) {
    case color::black:  return 0;
    case color::red: return 1;
    case color::green: return 2;
    case color::yellow: return 3;
    case color::blue: return 4;
    case color::magenta: return 5;
    case color::cyan: return 6;
    case color::white: return 7;
    default:    unreachable();
    }
}

void fg_color::print(ostream& out, string attr) const {
    char color_attr[16];
    sprintf(color_attr, "\e[]%2dn", 30+ansi_color_code(this->c));
    this->child->print(out, attr);
}

void bg_color::print(ostream& out, string attr) const {
    char color_attr[16];
    sprintf(color_attr, "\e[]%2dn", 40+ansi_color_code(this->c));
    this->child->print(out, attr);
}