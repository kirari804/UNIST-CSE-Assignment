#ifndef SHAPE_H
#define SHAPE_H

class shape {
public:
    virtual double area() const=0; //virtual method that can make change in child class
};

class triangle: public shape{  //triangle is a child of shape
    double base, height;
public:
    triangle(double b, double h): base(b), height(h) {}
    double area() const { return this->base* this->height *2;}
};

class circle: public shape { // circle is a child of shape
    double radius;
public:
    circle(double r): radius(r) {}
    double area() const {return 3.14 * this->radius * this->radius;}
};

class square: public shape { // circle is a child of shape
    double side;
public:
    square(double s): side(s) {}
    double area() const {return this->side*this->side;}
};


#endif