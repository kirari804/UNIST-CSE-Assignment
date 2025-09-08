#ifndef TEXT_H
#define TEXT_H
#include <iostream>
#include <string>


using namespace std;

class text { //parent class
public:
    virtual ~text();
    void print(ostream& out){ this->print(out, " ");}
    virtual void print(ostream&, string) const = 0;
};

class plain:public text {
    string s;
public:
    plain(string s): s(s) {}
    void print(ostream& out, string attr) const override  { out << attr << s;}
};

class concat:public text {
    text* left; //class-based polymorphism
    text* right;
public:
    concat(text* l, text* r): left(l), right(r) {}
    ~concat() {delete this->left; delete this->right;}
    concat(concat const&) = delete;
    concat& operator=(concat const&) = delete;
    void print(ostream&, string ) const override;
};

class bold:public text {
    text* child;
public:
    bold(text* c): child(c) {}
    ~bold() {delete this->child;}
    bold operator=(bold const&) = delete;
    void print(ostream&, string ) const override;
};

class passthrough:public text {
    text* child;
    passthrough(text* c): child(c) {}
public:
    ~passthrough();
};

enum class color {black, red, green, yellow, blue, magenta, cyan, white};

class fg_color:public text {
    text* child;
    color c;
public:
    fg_color(text* child, color c): child(child), c(c) {};
    ~fg_color() {delete this->child;}
    void print(ostream&, string) const override;
 };

class bg_color:public text {
    text* child;
    color c;
public:
    bg_color(text* child, color c): child(child), c(c){};
    void print(ostream&, string) const override;
};
#endif


