#include<stdio.h>
#include<stdlib.h>
#include<time.h>

void merge(int* array,int* temp,int left,int boundary,int right)
{
    int mark_left=left,mark_right=boundary;
    for (int mark_temp = left; mark_temp <= right; mark_temp++) 
    {
        if (mark_left <= boundary - 1 && mark_right <= right) 
        {
            if (array[mark_left] <= array[mark_right])
                temp[mark_temp] = array[mark_left++];
            else
                temp[mark_temp] = array[mark_right++];
        }
        else
        {
            if (mark_left > boundary - 1)
            {
                while (mark_right <= right) temp[mark_temp++]=array[mark_right++];
                break;
            }
            else
            {
                while (mark_left <= boundary-1) temp[mark_temp++]=array[mark_left++];
                break;
            }
        }
    }
    for(int i=left;i<=right;i++) array[i]=temp[i];
}

void m_sort(int* array,int* temp,int left,int right)
{
    if(left<right)
    {
        int center=(left+right)/2;
        m_sort(array,temp,left,center);
        m_sort(array,temp,center+1,right);
        merge(array,temp,left,center+1,right);
    }
}

void merge_sort(int* array,int N) 
{
    int *temp;
    if((temp = (int*)malloc(N*sizeof(int))))
    {
        m_sort(array,temp,0,N-1);
        free(temp);
    }
    else
    {
      printf("Error!Lack of space\n");
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

    merge_sort(array,N);

    for(int i=0;i<N;i++)
    {
        printf("%d ",array[i]);
    }
}