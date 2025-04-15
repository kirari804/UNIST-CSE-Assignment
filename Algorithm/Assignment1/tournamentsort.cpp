#include <iostream>
#include <climits>
using namespace std;

// Function to build the initial tournament tree
void buildTournament(int tree[], int n) {
    for (int i = n - 2; i >= 0; i--) {
        tree[i] = min(tree[2 * i + 1], tree[2 * i + 2]);
    }
}

// Function to replay the tournament after removing the current winner
void replay(int tree[], int n, int index, int value) {
    index += n - 1; // Move to leaf node
    tree[index] = value; // Replace value

    // Bubble up the changes
    while (index > 0) {
        int parent = (index - 1) / 2;
        int left = 2 * parent + 1;
        int right = 2 * parent + 2;
        tree[parent] = min(tree[left], tree[right]);
        index = parent;
    }
}

// Function to find the index of the current winner in the original array
int findWinnerIndex(int tree[], int n, int arr[]) {
    int index = 0;
    while (index < n - 1) {
        int left = 2 * index + 1;
        int right = 2 * index + 2;
        index = (tree[left] == tree[index]) ? left : right;
    }
    return index - (n - 1); // Convert leaf index to arr index
}

// Tournament Sort
void tournamentSort(int arr[], int n) {
    int treeSize = 2 * n - 1;
    int* tree = new int[treeSize];

    // Copy array into leaf nodes
    for (int i = 0; i < n; i++) {
        tree[n - 1 + i] = arr[i];
    }

    // Build tournament tree
    buildTournament(tree, n);

    // Extract winners one by one
    for (int i = 0; i < n; i++) {
        int winner = tree[0];
        int winnerIndex = findWinnerIndex(tree, n, arr);
        arr[i] = winner;

        // Set winner's leaf to INT_MAX (so it's not picked again)
        replay(tree, n, winnerIndex, INT_MAX);
    }

    delete[] tree;
}

void printArray(int A[], int size) 
{  
    for (size_t i=size/2; i < size; i++) 
        cout << A[i] <<endl;
} 



int main() {
    size_t size;
    cin >>size;
    int *arr = new int[size]; 

    for (size_t i = 0; i < size ; i++)
        cin >> arr[i];
    cout << size <<endl;
    for (size_t i=0; i < size/2; i++) 
        cout << arr[i] <<endl;
    tournamentSort(arr+size/2, size/2);
    printArray(arr, size); 
    return 0;
}