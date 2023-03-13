#include <stdio.h>
#include <math.h>

#define D 1000000

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

    printf("%f\n",result);
}

// Double a number
int double_number(int number)
{
    int result = number * 2;
    printf("%d", result);
}