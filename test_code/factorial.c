int factorial(int n) {
    if(n == 0) {
        return 1;
    }
    return factorial(n-1) * n;
}
int main(int argc, char** argv) {
    int a = factorial(5);
    int b = factorial(0);
    return a;
}