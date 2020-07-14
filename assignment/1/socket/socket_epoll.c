#include <signal.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>
#include<errno.h>

#include<sys/socket.h>
#include<sys/types.h>
#include<sys/epoll.h>
#include<netinet/in.h>
#include<unistd.h>
#include<fcntl.h>

#define LISTEN_PORT 8080
#define MAX_NUM 128
#define CLIENTS_NUM MAX_NUM-1
#define BUFF_SIZE 1024
#define MAX_PROCESS_EVENTS  10  //最大处理事件数

struct client{
    FILE* the_file;             //filefd
    int fd;                     //socketfd
    int status;
    char http_buff[BUFF_SIZE]; //请求报文
    char file_buff[BUFF_SIZE]; //读文件缓存
    struct sockaddr_in address; //地址
};

int main_epoll; //!!!epoll
int addrlen=sizeof(struct sockaddr_in); //功能用
struct sockaddr_in client_addr; //服务器地址

char* response_head="HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\n\r\n";
char* error_head="HTTP/1.1 404 Not Found";
char file_url[64];

int init_server()
{
    struct sockaddr_in server_addr; //服务器地址
    server_addr.sin_port=htons(LISTEN_PORT);
    server_addr.sin_family=AF_INET;
    server_addr.sin_addr.s_addr=htonl(INADDR_ANY);

    int flag,my_listen_socketfd=socket(AF_INET,SOCK_STREAM|SOCK_NONBLOCK,0);
    flag=bind(my_listen_socketfd,(struct sockaddr*)&server_addr,sizeof(struct sockaddr));
    flag=listen(my_listen_socketfd,10);
    if(!flag) printf("Successfully bind and listen!\n");

    main_epoll = epoll_create(MAX_NUM);
    struct epoll_event the_event;
    the_event.data.ptr=NULL;    //事件内data为空指针，表示为服务器事件
    the_event.events=EPOLLIN;
    epoll_ctl(main_epoll,EPOLL_CTL_ADD,my_listen_socketfd,&the_event);  //添加监听套接字

    return my_listen_socketfd;
}

void identify(char* buff,char**method,char**url)
{
    char *headline=strtok(buff,"\r\n");             //获得请求行
    *method=strtok(headline," ");                    //获取请求方法
    *url=strtok(NULL," ");                           //获取url

    file_url[0]='\0';

    strcat(file_url,"./data");
    strcat(file_url,*url);                           //获取请求文件路径

    // printf("\nasdsda:%s\n",file_url);
}

void close_client(struct client* R)
{
    epoll_ctl(main_epoll,EPOLL_CTL_DEL,R->fd,NULL);
    close(R->fd);
    free(R);
}


void not_found(struct client* R)
{
    send(R->fd,error_head,strlen(error_head),0);
    close_client(R);
}

int test=0;

int main()
{
    signal(SIGPIPE, SIG_IGN);   //避免传输中断产生的SIGPIPE信号结束程序

    int server_fd=init_server();
    struct epoll_event the_events[MAX_PROCESS_EVENTS];

    while (1)
    {
        // printf("\nwaiting...\n");
        int num;
        num=epoll_wait(main_epoll,the_events,MAX_PROCESS_EVENTS,-1);
        // printf("事件数: %d\n",num);
        for(int i=0;i<num;i++)
        {
            if(the_events[i].data.ptr==NULL)    //服务器接收到accept
            {
                int j;  //接受队列中的连接
                struct epoll_event add_event;
                while ((j=accept(server_fd,(struct sockaddr*)&client_addr,(socklen_t *)&addrlen))!=-1)
                {
                    struct client *new_client=(struct client*)malloc(sizeof(struct client));
                    new_client->fd=j;
                    new_client->status=0;
                    fcntl(j, F_SETFL, fcntl(j, F_GETFL, 0) | O_NONBLOCK);//设置为非阻塞
                    memcpy(&new_client->address,&client_addr,sizeof(struct sockaddr_in));
                    add_event.events=EPOLLIN;
                    add_event.data.ptr=new_client;
                    epoll_ctl(main_epoll,EPOLL_CTL_ADD,j,&add_event);  //添加监听套接字
                    // printf("%d 增加客户端链接\n",i);
                }
            }
            else if (the_events[i].events&EPOLLIN)
            {
                // printf("%d 接收信息...\n",i);
                struct client* HHH=the_events[i].data.ptr;
                struct epoll_event add_event;
                int flag;
                flag=recv(HHH->fd,HHH->http_buff,BUFF_SIZE,0);
                if(flag==0||flag==-1)
                {
                    // printf("Continue\n");
                    close_client(HHH);
                    continue;
                }
                // printf("%ld",strlen(HHH->http_buff));


                char* method,*url;
                identify(HHH->http_buff,&method,&url);

                // printf("\nmethod:%s;url:%s;file_url:%s\n",method,url,file_url); //验证程序执行

                if(strcmp(method,"GET")) HHH->status=-1;

                // printf("%s ",file_url);
                HHH->the_file=fopen(file_url,"rb");
                // printf("%p\n",HHH->the_file);
                add_event.events=EPOLLOUT;
                add_event.data.ptr=HHH;
                epoll_ctl(main_epoll,EPOLL_CTL_MOD,HHH->fd,&add_event);
            }
            else if (the_events[i].events&EPOLLOUT)
            {
                // printf("%d 发送\n",i);
                struct client* HHH=the_events[i].data.ptr;
                // printf("%d \n",HHH->status);
                switch (HHH->status)
                {
                case -1:    //方法不对
                    not_found(HHH);
                    break;

                case 0:     //方法正确，判断是否存在，返回响应报头
                    if(!HHH->the_file)  //文件不存在
                    {
                        not_found(HHH);
                        // printf("文件不存在发送成功!\n");
                    }
                    else
                    {
                        send(HHH->fd,response_head,strlen(response_head),0);
                        HHH->status=1;
                    }
                    break;

                case 1:     //继续传输文件
                    if(!feof(HHH->the_file))
                    {
                        fread(HHH->file_buff,1,BUFF_SIZE,HHH->the_file);
                        if(send(HHH->fd,HHH->file_buff,BUFF_SIZE,0)<0){
                            int the_errno =errno;
                            if(errno==EPIPE){
                                close_client(HHH);
                            }
                            else if(errno==EAGAIN||errno==EWOULDBLOCK)
                            {
                                HHH->status=2;  //重试一次
                            }
                        }
                    }
                    else
                    {   //传完了
                        close_client(HHH);
                    }
                    break;
                case 2:
                    if(send(HHH->fd,HHH->file_buff,BUFF_SIZE,0)>=0){
                        HHH->status=1;
                    }
                    else
                    {
                        close_client(HHH);
                    }
                    break;
                }
            }
        }
    }
    
    int flag=0;
    flag+=close(main_epoll);
    flag+=close(server_fd);
    if(!flag) printf("\nSuccessfully closed\n");
    
    return 0;
}