/* Simple example: factorial function */

int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int x;
    x = 5;
    int result;
    result = factorial(x);
    return result;
}
