#include<stdio.h>
#include<stdlib.h>
typedef struct node tree_node;
typedef struct q_node queue_node;
struct node
{
    int data;
    struct node* left;
    struct node* right;
}*the_root;
struct q_node
{
    tree_node* data;
    queue_node* next;
};

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

void append(queue_node* the_queue,tree_node* add)
{
    queue_node* p=the_queue;
    for(;p->next!=NULL;p=p->next);
    p->next=(queue_node*)malloc(sizeof(queue_node));
    p->next->data=add;
    p->next->next=NULL;
    return;
}

int main()
{
    the_root=(tree_node*)malloc(sizeof(tree_node));
    my_init(the_root);

    queue_node* queue=(queue_node*)malloc(sizeof(queue_node));
    queue->data=the_root;
    queue->next=NULL;
    while (queue!=NULL)
    {
        queue_node* new=(queue_node*)malloc(sizeof(queue_node));
        queue_node *temp=queue,*head;
        new->next=NULL;
        for(;queue!=NULL;queue=queue->next)/* 遍历队列输出，保留非NULL子节点到new中 */
        {
            tree_node *A=queue->data;
            printf("%d ", A->data);
            if(A->left!=NULL) append(new,A->left);
            if(A->right!=NULL) append(new,A->right);
        }
        for(head=temp;head->next!=NULL;)
        {
            temp=head->next;
            free(head);
            head=temp;
        }
        free(head);
        queue=new->next;
    }
    
}