#include<stdio.h>
#include<stdlib.h>
#include<time.h>

void swap(int*a,int*b)
{
    int temp=*b;
    *b = *a;
    *a = temp;
}

int median3(int* array,int left,int right)
{
    int center = (left+right)/2;
    if(array[left]>array[center]) swap(&array[left],&array[center]);
    if(array[left]>array[right]) swap(&array[left],&array[right]);
    if(array[center]>array[right]) swap(&array[center],&array[right]);
    
    swap(&array[center],&array[right-1]);
    return array[right-1];
}

void q_sort(int* array,int left,int right)
{
    /* 枢纽元选取用三值中值 */
    int i=left,j=right-1,key;
    if(i<j)
    {
        key = median3(array,left,right);
        for(;;)
        {
            while (array[++i]<key);
            while (array[--j]>key);
            if(i<j) swap(&array[i],&array[j]);
            else break;
        }
        swap(&array[i],&array[right-1]);

        q_sort(array,left,i-1);
        q_sort(array,i+1,right);
    }
    else
    {
        if(array[left]>array[right]) swap(&array[left],&array[right]);
        return;
    }
}

void quick_sort(int* array,int N)
{
    q_sort(array,0,N-1);
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
        array[i]=rand()%20-10;
    }
    quick_sort(array,N);

    for(int i=0;i<N;i++)
    {
        printf("%d ",array[i]);
    }
}