#include <climits>
#include <cstdlib>
#include <ctime>
#include <iostream>
#include <cassert>

 
int main()
{
    // use current time as seed for random generator
    std::srand(std::time(NULL));
 
    size_t n;
    std::cin >> n;
    std::cout << n << std::endl;
    for (int i = 0; i <n ; i++) {
        std::cout << std::rand()  << std::endl;
    }

}