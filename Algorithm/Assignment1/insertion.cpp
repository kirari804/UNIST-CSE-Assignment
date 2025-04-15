#include <iostream>
#include <string>

using namespace std;

void insertionSort(int arr[], int n)
{
    int i, j;
    for (i = 1; i < n; i++)
    {
        int var = arr[i]; //Taken first element as sorted
        for (j = i - 1; j >= 0; j--)
        {
            //Making comparisons
            if (arr[j] > var)
            {
                //Shifting elements
                arr[j + 1] = arr[j];
            }
            else
            {
                break;
            }
        }
        arr[j + 1] = var;
    }
}

void printArray(int A[], int size) 
{  
    for (size_t i=0; i < size; i++) 
        cout << A[i] <<endl;
} 

int main() {
    size_t size;
    cin >>size;
    int *arr = new int[size]; 
    for (size_t i = 0; i < size ; i++)
        cin >> arr[i];
  
    insertionSort(arr, size); 
    printArray(arr, size); 
    return 0;
}