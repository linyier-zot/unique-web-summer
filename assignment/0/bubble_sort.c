#include<stdio.h>
#include<stdlib.h>
#include<time.h>

void bubble_sort(int* array,int N)
{
    int temp;
    for(int i=0;i<N-1;i++)
    {
        for(int j=0;j<N-1-i;j++)
        {
            if(array[j]>array[j+1])
            {
                temp=array[j+1];
                array[j+1]=array[j];
                array[j]=temp;
            }
        }
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

    bubble_sort(array,N);

    for(int i=0;i<N;i++)
    {
        printf("%d ",array[i]);
    }
}