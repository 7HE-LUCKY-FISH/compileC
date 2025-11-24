#include <stdio.h>

int main(){
    int i;
    int res =0;
    int sum =0;

    for(i = 1; i < 10; i++){
        res += i;
    }

    while (sum < 10){
        sum += 1;
    }
    printf("res: %d, sum: %d\n", res, sum);
    return res;
}