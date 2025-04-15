#include <iostream>
#include <cmath>
#include <climits>
#include <vector>

using namespace std;
const int GAP = -1;
size_t binarySearch(int val, int* S, size_t size) {
    size_t low = 0, high = size;
    while (low < high) {
        size_t mid = (low + high) / 2;

        if (S[mid] == GAP) {
            // Scan forward
            size_t i = mid + 1;
            while (i < high && S[i] == GAP) ++i;
            if (i < high && S[i] <= val) {
                low = i + 1;
                continue;
            }

            // Scan backward
            i = mid;
            while (i > low && S[i - 1] == GAP) --i;
            if (i > low && S[i - 1] > val) {
                high = i - 1;
                continue;
            }

            return mid;
        } else if (S[mid] > val) {
            high = mid;
        } else {
            low = mid + 1;
        }
    }
    return low;
}



// void rebalance(int* S, size_t allocSize) {
//     int* temp = new int[allocSize];
//     size_t count = 0;

//     // First pass: collect all real values
//     for (size_t i = 0; i < allocSize; ++i) {
//         if (S[i] != GAP)
//             temp[count++] = S[i];
//     }

//     // Clear S with all GAPs
//     for (size_t i = 0; i < allocSize; ++i)
//         S[i] = GAP;

//     // Spread the real values with gaps between them
//     if (count == 0) {
//         delete[] temp;
//         return;
//     }

//     double gap_ratio = static_cast<double>(allocSize) / count;
//     for (size_t i = 0; i < count; ++i) {
//         size_t index = static_cast<size_t>((i + 1) * gap_ratio) - 1;
//         if (index >= allocSize) break;
//         S[index] = temp[i];
//     }

//     delete[] temp;
// }

void rebalance(int* S, size_t allocSize) {
    // Move valid entries to the front while respecting gaps
    int* temp = new int[allocSize];
    size_t j = 0;

    // First pass: move valid values to a temporary array
    for (size_t i = 0; i < allocSize; ++i) {
        if (S[i] != GAP)
            temp[j++] = S[i];
    }

    // Second pass: copy valid values back into S, leaving gaps for new inserts
    for (size_t i = 0; i < allocSize; ++i) {
        if (i < j)
            S[i] = temp[i];
        else
            S[i] = GAP;
    }

    delete[] temp;
}

void librarySort(int* A, size_t n) {
    if (n <= 1) return;

    size_t allocSize = n * 8;
    int* S = new int[allocSize];
    for (size_t i = 0; i < allocSize; ++i)
        S[i] = GAP;

    S[allocSize / 2] = A[0];  // Start inserting A[0] in the middle of S[]
    size_t inserted = 1;

    for (size_t phase = 2; inserted < n; phase *= 2) {
        rebalance(S, allocSize);

        size_t insertsThisPhase = min(phase / 2, n - inserted);
        for (size_t j = 0; j < insertsThisPhase; ++j) {
            int val = A[inserted++];
            size_t pos = binarySearch(val, S, allocSize);

            // Shift right to insert at the correct position
            size_t end = pos;
            while (end < allocSize && S[end] != GAP)
                ++end;
            for (size_t k = end; k > pos; --k)
                S[k] = S[k - 1];

            S[pos] = val;
        }
    }

    // Copy sorted values back to A[]
    size_t j = 0;
    for (size_t i = 0; i < n; ++i) {
        while (S[j] == GAP) ++j;
        A[i] = S[j++];
    }

    delete[] S;
}


void printArray(int A[], int size) 
{  
    for (size_t i=0; i < size; i++) 
        cout << A[i] <<endl;
} 


int main() {
    size_t size;
    cin >> size;
    int* arr = new int[size];
    for (int i = 0; i < size; i++)
        cin >> arr[i];

    librarySort(arr, size);
    printArray(arr, size);
    return 0;
}