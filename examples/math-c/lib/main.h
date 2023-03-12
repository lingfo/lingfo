#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#define N 1000
#define D 100000000

// Iteratively adds the product of sine(x + i) and cosine(y + i) for i from 1 to 1,000,000.

double itt_add()
{
    double x = 1.0;
    double y = 2.0;
    double result = 0.0;
    int i;

    for (i = 1; i <= 1000000; i++) {
        result += sin(x + i) * cos(y + i);
    }

    return result;
}




void matrix_multiply()
{
    double A[N][N], B[N][N], C[N][N];
    int i, j, k;

    // Initialize matrices A and B with random values
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            A[i][j] = rand() % 10;
            B[i][j] = rand() % 10;
        }
    }

    // Perform matrix multiplication
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            C[i][j] = 0;
            for (k = 0; k < N; k++) {
                C[i][j] += A[i][k] * B[k][j];
            }
        }
    }
}


double array_sum()
{
    double *arr;
    int i;
    double sum = 0.0;

    // Allocate memory for the array
    arr = (double *) malloc(N * sizeof(double));

    // Initialize the array with random values
    for (i = 0; i < D; i++) {
        arr[i] = rand() % 10;
    }

    // Calculate the sum of the array
    for (i = 0; i < D; i++) {
        sum += arr[i];
    }

    free(arr);

    printf("%d", sum);
}