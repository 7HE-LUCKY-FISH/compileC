/* 
 * Nested control structures
 * Demonstrates if-else and while nested together
 */

int main() {
    int i;
    int j;
    int count;
    
    count = 0;
    i = 0;
    
    while (i < 5) {
        if (i > 2) {
            j = 0;
            while (j < i) {
                count = count + 1;
                j = j + 1;
            }
        } else {
            count = count + i;
        }
        i = i + 1;
    }
    
    return count;
}
