#include<stdio.h>
#include<stdlib.h>

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

int main()
{
    heap* test_heap=(heap*)malloc(sizeof(heap));
    Init(20, test_heap);

    int cmd,date;
    while (1)
    {
        printf("指令：1——Insert;2——ShowMin;3——DeleteMin;4——exit\n");
        scanf("%d",&cmd);
        if(cmd==4) break;
        switch (cmd)
        {
            case 1:
                printf("Insert:");
                scanf("%d", &date);
                Insert(test_heap, date);
                break;
            case 2:
                if(IsEmpty(test_heap)) printf("heap is empty!\n");
                else ShowMin(test_heap);
                break;     
            case 3:
                if(IsEmpty(test_heap)) printf("heap is empty!\n");
                else DeleteMin(test_heap);
                break;
            default:
                printf("cmd error!\n");
        }
    }
}