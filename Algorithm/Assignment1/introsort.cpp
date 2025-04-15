#include <iostream>
#include <cmath>

using namespace std;
int Partition(int* a, int left, int right) {
	int pivot = a[right];
	int temp;
	int i = left;

	for (int j = left; j < right; ++j)
	{
		if (a[j] <= pivot)
		{
			temp = a[j];
			a[j] = a[i];
			a[i] = temp;
			i++;
		}
	}

	a[right] = a[i];
	a[i] = pivot;

	return i;
}

void QuickSort(int* a, int l, int r) {
	if (left < right)
	{
		int q = Partition(a, l, r);
		QuickSort(a, l, q - 1);
		QuickSort(a, q + 1, r);
	}
}

int max (int *a, int n, int i, int j, int k) {
    int m = i;
    if (j < n && a[j] > a[m]) {
        m = j;
    }
    if (k < n && a[k] > a[m]) {
        m = k;
    }
    return m;
}

void downheap (int *a, int n, int i) {
    while (1) {
        int j = max(a, n, i, 2 * i + 1, 2 * i + 2);
        if (j == i) {
            break;
        }
        int t = a[i];
        a[i] = a[j];
        a[j] = t;
        i = j;
    }
}

void heapsort (int *a, int n) {
    int i;
    for (i = (n - 2) / 2; i >= 0; i--) {
        downheap(a, n, i);
    }
    for (i = 0; i < n; i++) {
        int t = a[n - i - 1];
        a[n - i - 1] = a[0];
        a[0] = t;
        downheap(a, n - i - 1, 0);
    }
}

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


void IntroSort(int* a, int n) {
	int partitionSize = Partition(a, 0, n - 1);

	if (partitionSize < 16)
	{
		insertionSort(a , n);
	}
	else if (partitionSize >(2 * log(n)))
	{
		heapsort(a, n);
	}
	else
	{
		QuickSort(a, 0, n - 1);
	}
}

void printArray(int A[], int size) 
{  
    for (size_t i=0; i < size; i++) 
        cout << A[i] <<endl;
} 

// void printArray(int A[], int size) 
// {  
//     for (size_t i = size-1; i >=0; i--) 
//         cout << A[i] <<endl;
// } 

int main() {
    size_t size;
    cin >>size;
    int *arr = new int[size]; 
    for (size_t i = 0; i < size ; i++)
        cin >> arr[i];
  
    IntroSort(arr, size);
    printArray(arr, size); 
    return 0;
}