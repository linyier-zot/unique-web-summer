#include<stdio.h>
#include<stdlib.h>
#include<time.h>

void insertion_sort(int* array,int N)
{
    int temp,i;
    for(int p=1;p<N;p++)
    {
        temp=array[p];
        for(i=p;i>0&&array[i-1]>temp;i--) array[i]=array[i-1];
        array[i]=temp;
    }
}

int main()
{
    int N,i;
    printf("设置大小:\n");
    scanf("%d", &N);
    srand((unsigned)time(NULL));
    int array[N];
    for(i=0;i<N;i++)
    {
        array[i]=rand()%5000-2500;
    }

    insertion_sort(array,N);

    for(int i=0;i<N;i++)
    {
        printf("%d ",array[i]);
    }
}