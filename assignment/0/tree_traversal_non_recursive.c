#include<stdio.h>
#include<stdlib.h>
typedef struct node tree_node;
typedef struct stack_defi node;
struct node
{
    int data;
    struct node* left;
    struct node* right;
}*the_root;
struct stack_defi
{
    tree_node* data;
    node* next;
};
/* 栈的链表实现 */
int IsEmpty(node* s)
{
    return s->next==NULL;
}
void push(node* stack,tree_node* data)
{
    node* new=(node*)malloc(sizeof(node));
    new->data=data;
    new->next=stack->next;
    stack->next=new;
}
void pop(node* stack)
{
    if(IsEmpty(stack)) printf("stack is empty!\n");
    else
    {
        node* temp=stack->next->next;
        free(stack->next);
        stack->next=temp;
    }
}
tree_node* top(node* stack)
{
    if(stack->next==NULL) printf("stack is empty!\n");
    else return stack->next->data;
    return NULL;
}

void my_init(tree_node* root)   
{   /* 直接手动创棵树 */
    root->data=1;
    root->left=(tree_node*)malloc(sizeof(tree_node));
    root->left->data=2;
    root->left->left=(tree_node*)malloc(sizeof(tree_node));
    root->left->right=(tree_node*)malloc(sizeof(tree_node));
    root->left->left->data=4;
    root->left->left->left=NULL;
    root->left->left->right=NULL;
    root->left->right->data=5;
    root->left->right->left=NULL;
    root->left->right->right=NULL;
    root->right=(tree_node*)malloc(sizeof(tree_node));
    root->right->data=3;
    root->right->left=(tree_node*)malloc(sizeof(tree_node));
    root->right->right=(tree_node*)malloc(sizeof(tree_node));
    root->right->left->data=6;
    root->right->left->left=NULL;
    root->right->left->right=NULL;
    root->right->right->data=7;
    root->right->right->left=NULL;
    root->right->right->right=NULL;
}

int main()
{
    the_root=(tree_node*)malloc(sizeof(tree_node));
    my_init(the_root);

    node* stack=(node*)malloc(sizeof(node));
    stack->next=NULL;

    tree_node* last_pop=the_root;
    printf("先序:");
    push(stack,the_root);
    printf("%d ", the_root->data);
    while (!IsEmpty(stack))
    {
        tree_node* the_top=top(stack);
        if(the_top->left!=NULL&&the_top->left!=last_pop&&the_top->right!=last_pop)
        {
            push(stack,the_top->left);
            printf("%d ", the_top->left->data);
        }
        else if (the_top->right!=NULL&&the_top->right!=last_pop&&(the_top->left==NULL||the_top->left==last_pop))
        {
            push(stack, the_top->right);
            printf("%d ",the_top->right->data);
        }
        else
        {
            last_pop=top(stack);
            pop(stack);
        }
    }

    printf("\n中序:");
    push(stack,the_root);
    last_pop=the_root;
    while (!IsEmpty(stack))
    {
        tree_node* the_top=top(stack);
        if(the_top->left!=NULL&&the_top->left!=last_pop&&the_top->right!=last_pop)
        {
            push(stack,the_top->left);
        }
        else if (the_top->right!=NULL&&the_top->right!=last_pop&&(the_top->left==NULL||the_top->left==last_pop))
        {
            push(stack, the_top->right);
            printf("%d ",the_top->data);
        }
        else
        {
            pop(stack);
            last_pop=the_top;
            if(the_top->right==NULL)
                printf("%d ",the_top->data);
        }
    }

    printf("\n后序:");
    push(stack,the_root);
    last_pop=the_root;
    while (!IsEmpty(stack))
    {
        tree_node* the_top=top(stack);
        if(the_top->left!=NULL&&the_top->left!=last_pop&&the_top->right!=last_pop)
        {
            push(stack,the_top->left);
        }
        else if (the_top->right!=NULL&&the_top->right!=last_pop&&(the_top->left==NULL||the_top->left==last_pop))
        {
            push(stack, the_top->right);
        }
        else
        {
            pop(stack);
            last_pop=the_top;
            printf("%d ",the_top->data);
        }
    }
    putchar('\n');

}