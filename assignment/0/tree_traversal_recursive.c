#include<stdio.h>
#include<stdlib.h>
typedef struct node tree_node;
struct node
{
    int data;
    struct node* left;
    struct node* right;
}*the_root;

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
void list(tree_node* p,int mode)
{
    if(p)
    {
        switch (mode)
        {
        case 1:/* 先序 */
            printf("%d ",p->data);
            list(p->left,mode);
            list(p->right,mode);
            break;
        case 2:/* 中序 */
            list(p->left,mode);
            printf("%d ",p->data);
            list(p->right,mode);
            break;
        case 3:/* 后序 */
            list(p->left,mode);
            list(p->right,mode);
            printf("%d ",p->data);
            break;
        }
       
    }
}

int main()
{
    the_root=(tree_node*)malloc(sizeof(tree_node));
    my_init(the_root);
    printf("\n前序：");
    list(the_root,1);
    printf("\n中序：");
    list(the_root,2);
    printf("\n后序：");
    list(the_root,3);
}
