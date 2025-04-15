#include <iostream>
#include <string>

using namespace std;
void quicksort(int *A, int len) {
  if (len < 2) return;

  int pivot = A[len / 2];

  int i, j;
  for (i = 0, j = len - 1; ; i++, j--) {
    while (A[i] < pivot) i++;
    while (A[j] > pivot) j--;

    if (i >= j) break;

    int temp = A[i];
    A[i]     = A[j];
    A[j]     = temp;
  }

  quicksort(A, i);
  quicksort(A + i, len - i);
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
  
    quicksort(arr, size); 
    printArray(arr, size); 
    return 0;
}