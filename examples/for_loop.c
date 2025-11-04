/* 
 * For loop example
 * Demonstrates for loop syntax
 */

int main() {
    int sum;
    int i;
    
    sum = 0;
    
    for (i = 1; i < 11; i = i + 1) {
        sum = sum + i;
    }
    
    return sum;
}
