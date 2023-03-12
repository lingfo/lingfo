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

    for (i = 1; i <= D; i++) {
        result += sin(x + i) * cos(y + i);
    }

    printf("%d\n",result);
}




void matrix_multiply()
{
    double **A, **B, **C;
    int i,j, k;

    // Allocate memory for matrices A and B
    A = (double **)malloc(N * sizeof(double *));
    B = (double **)malloc(N * sizeof(double *));
    for (i = 0; i < N; i++) {
        A[i] = (double *)malloc(N * sizeof(double));
        B[i] = (double *)malloc(N * sizeof(double));
    }

    // Initialize matrices A and B with random values
    for (i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
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

    // Print the resulting matrix
    printf("Resulting matrix:\n");
    for (i = 0; i < N; i++) {
        for (j = 0; j < N; j++) {
            printf("%f ", C[i][j]);
        }
        printf("\n");
    }

    // Free the allocated memory
    for (i = 0; i < N; i++) {
        free(A[i]);
        free(B[i]);
    }
    free(A);
    free(B);
}


double array_sum()
{
    double *arr;
    int i;
    double sum = 0.0;

    // Allocate memory for the array
    arr = (double *) malloc(D * sizeof(double));

    // Initialize the array with random values
    for (i = 0; i < D; i++) {
        arr[i] = rand() % 10;
    }

    // Calculate the sum of the array
    for (i = 0; i < D; i++) {
        sum += arr[i];
    }

    free(arr);

    printf("%d\n", sum);
}