#include<stdio.h>
#include<stdlib.h>

typedef struct node_defi node;
struct node_defi
{
    int data;
    node* next;
};

int IsEmpty(node* s)
{
    return s->next==NULL;
}

void push(node* stack,int data)
{
    node* new=(node*)malloc(sizeof(node));
    new->data=data;
    new->next=stack->next;
    stack->next=new;
    printf("Successfully push %d\n",data);
}
void pop(node* stack)
{
    if(IsEmpty(stack)) printf("stack is empty!\n");
    else
    {
        node* temp=stack->next->next;
        free(stack->next);
        stack->next=temp;
        printf("Successfully pop!\n");
    }
}
void top(node* stack)
{
    if(stack->next==NULL) printf("stack is empty!\n");
    else printf("top:%d\n",stack->next->data);
}


int main()
{
    int cmd,date;
    node* test_stack=(node*)malloc(sizeof(node));
    test_stack->next=NULL;
    while (1)
    {
        printf("指令：1——push;2——pop;3——top;4——exit\n");
        scanf("%d",&cmd);
        if(cmd==4) break;
        switch (cmd)
        {
        case 1:
            printf("push:");
            scanf("%d", &date);
            push(test_stack,date);
            break;
        case 2:
            pop(test_stack);
            break;        
        case 3:
            top(test_stack);
            break;
        default:
            printf("error");
        }
    }
}