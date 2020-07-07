#include<stdio.h>
#include<stdlib.h>
#include<limits.h>
#include<time.h>

typedef struct heap_defi heap;
struct heap_defi
{
    int max_size;
    int size;
    int *elements;
};
int IsEmpty(heap* the)
{
    return the->size==0;
}
int IsFull(heap* the)
{
    return the->max_size==the->size;
}
void Init(int max,heap* the_heap)
{
    the_heap->max_size=max;
    the_heap->elements=(int*)malloc((max+1)*sizeof(int));
    the_heap->size=0;
    the_heap->elements[0]=INT_MIN;
}
void Insert(heap* the_heap,int date)
{
    int i;
    if(IsFull(the_heap))
    {
        printf("Full!!");
        return;
    }
    if(IsEmpty(the_heap))
    {
        the_heap->elements[1]=date;
        ++the_heap->size;
        return;
    }
    for(i=++the_heap->size;the_heap->elements[i/2]>date;i/=2) 
        the_heap->elements[i]=the_heap->elements[i/2];
    the_heap->elements[i]=date;
}
int DeleteMin(heap* theheap)
{
    int min,last,i,child;
    min=theheap->elements[1];
    last=theheap->elements[theheap->size--];

    for(i=1;i*2<=theheap->size;i=child)
    {
        child=i*2;
        if(child != theheap->size && theheap->elements[child+1] < theheap->elements[child]) child++;
        if(last>theheap->elements[child]) theheap->elements[i]=theheap->elements[child];
        else break;
    }
    theheap->elements[i]=last;
    return min;
}
void ShowMin(heap* the_heap)
{
    printf("Min in heap:%d\n",the_heap->elements[1]);
}
void heap_sort(int *array,int N)
{
    heap* test_heap=(heap*)malloc(sizeof(heap));
    Init(N, test_heap);
    for(int i=0;i<N;i++) Insert(test_heap,array[i]);
    for(int i=0;i<N;i++) array[i]=DeleteMin(test_heap);
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

    heap_sort(array,N);

    for(int i=0;i<N;i++)
    {
        printf("%d ",array[i]);
    }
    

}