#include <iostream>
#include <string>

using namespace std;
const int RUN = 32;
void merge(int arr[], int l, int m, int r) 
{ 
    int i, j, k; 
    int n1 = m - l + 1; 
    int n2 =  r - m; 
  
    /* create temp arrays */
    int L[n1], R[n2]; 
  
    /* Copy data to temp arrays L[] and R[] */
    for (i = 0; i < n1; i++) 
        L[i] = arr[l + i]; 
    for (j = 0; j < n2; j++) 
        R[j] = arr[m + 1+ j]; 
  
    /* Merge the temp arrays back into arr[l..r]*/
    i = 0; // Initial index of first subarray 
    j = 0; // Initial index of second subarray 
    k = l; // Initial index of merged subarray 
    while (i < n1 && j < n2) 
    { 
        if (L[i] <= R[j]) 
        { 
            arr[k] = L[i]; 
            i++; 
        } 
        else
        { 
            arr[k] = R[j]; 
            j++; 
        } 
        k++; 
    } 
  
    /* Copy the remaining elements of L[], if there 
       are any */
    while (i < n1) 
    { 
        arr[k] = L[i]; 
        i++; 
        k++; 
    } 
  
    /* Copy the remaining elements of R[], if there 
       are any */
    while (j < n2) 
    { 
        arr[k] = R[j]; 
        j++; 
        k++; 
    }
}


void insertionSort(int arr[], int l, int r)
{
    int i = l + 1;
    while (i <= r) {
        int temp = arr[i];
        int j = i-1;
        while (j >= l && arr[j] > temp) {
            arr[j+1] = arr[j];
            j = j-1;
        }
        arr[j+1] = temp;
        i = i+1;
    }
}

void timSort(int arr[], int n) {
    int i = 0;
    int size = RUN;
    int left = 0;
    while (i < n) {
        int temp = min(i+RUN-1, n-1);
        insertionSort(arr,i,temp);
        i = i+RUN;
    }
    while (size < n) {
        while (left < n) {
            int mid = left + size -1;
            int right = min(left + 2*size -1,n-1);
            if (mid < right)
                merge(arr,left,mid,right);
            left += 2*size;
        }
        left = 0;
        size = size*2;
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
  
    timSort(arr, size); 
    printArray(arr, size); 
    return 0;
}