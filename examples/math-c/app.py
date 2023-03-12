# pylint: disable=missing-module-docstring

import math
import random
import timeit

from sushipy.main import Sushi

D = 100000000
N = 1000


def py_itt_add():
    x = 1.0
    y = 2.0
    result = 0.0

    for i in range(1, D + 1):
        result += math.sin(x + i) * math.cos(y + i)

    print(result)


def py_array_sum():
    arr = [0.0] * D
    sum = 0.0

    # Initialize the array with random values
    for i in range(D):
        arr[i] = random.randint(0, 9)

    # Calculate the sum of the array
    for i in range(D):
        sum += arr[i]

    print(sum)


def py_matrix_multiply():
    # Matrices A, B, and C
    A = [[0 for _ in range(N)] for _ in range(N)]
    B = [[0 for _ in range(N)] for _ in range(N)]
    C = [[0 for _ in range(N)] for _ in range(N)]

    # Initialize matrices A and B with random values
    for i in range(N):
        for j in range(N):
            A[i][j] = random.randint(0, 9)
            B[i][j] = random.randint(0, 9)

    # Perform matrix multiplication
    for i in range(N):
        for j in range(N):
            for k in range(N):
                C[i][j] += A[i][k] * B[k][j]

    # Print the resulting matrix
    print("Resulting matrix:")
    for row in C:
        print(*row)


# Run benchmarks of our C code and the equivalent Python code
if __name__ == "__main__":
    Sushi()

    # sushi generates code for us to call in Python
    from out.main import *

    # Time the matrix_multiply() function
    matrix_multiply_time = timeit.timeit(
        "matrix_multiply()", setup="from __main__ import matrix_multiply", number=1
    )

    # Time the py_matrix_multiply() function
    py_matrix_multiply_time = timeit.timeit(
        "py_matrix_multiply()",
        setup="from __main__ import py_matrix_multiply",
        number=1,
    )

    # Time the array_sum() function
    array_sum_time = timeit.timeit(
        "array_sum()", setup="from __main__ import array_sum", number=3
    )

    # Time the py_array_sum() function
    py_array_sum_time = timeit.timeit(
        "py_array_sum()", setup="from __main__ import py_array_sum", number=3
    )

    # Time the itt_add() function
    itt_add_time = timeit.timeit(
        "itt_add()", setup="from __main__ import itt_add", number=3
    )

    # Time the py_itt_add() function
    py_itt_add_time = timeit.timeit(
        "py_itt_add()", setup="from __main__ import py_itt_add", number=3
    )

    # Print the results
    print("itt_add() took", itt_add_time, "seconds")
    print("py_itt_add() took", py_itt_add_time, "seconds")

    print("matrix_multiply() took", matrix_multiply_time, "seconds")
    print("py_matrix_multiply() took", py_matrix_multiply_time, "seconds")

    print("array_sum() took", array_sum_time, "seconds")
    print("py_array_sum() took", py_array_sum_time, "seconds")
