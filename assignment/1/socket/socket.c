#include <signal.h>
#include<stdio.h>
#include<stdlib.h>
#include<string.h>

#include <sys/epoll.h>
#include<sys/socket.h>
#include<sys/types.h>
#include<sys/wait.h>
#include<netinet/in.h>
#include<unistd.h>

#define LISTEN_PORT 8080
/* void kill_zombie(int sig)
{
    int status;
    while (waitpid(-1,&status,WNOHANG)>0);
    return;
}
 */


int main()
{
    pid_t pid;

    int my_listen_socketfd=socket(AF_INET,SOCK_STREAM,0),my_C_socketfd;
    struct sockaddr_in server_addr,client_addr;
    server_addr.sin_port=htons(LISTEN_PORT);
    server_addr.sin_family=AF_INET;
    server_addr.sin_addr.s_addr=htonl(INADDR_ANY);

    // printf("socketfd:%d\n",my_listen_socketfd);
    if(!bind(my_listen_socketfd,(struct sockaddr*)&server_addr,sizeof(struct sockaddr))) printf("bind successfully!\n");
    if(!listen(my_listen_socketfd,1)) printf("Listen successfully!\n");




    int addrlen=sizeof(struct sockaddr_in);
    // signal(SIGCHLD, kill_zombie);    
    signal(SIGCHLD,SIG_IGN);
    signal(SIGPIPE, SIG_IGN);

    while (1)
    {
        my_C_socketfd=accept(my_listen_socketfd,(struct sockaddr*)&client_addr,(socklen_t *)&addrlen);
        //等待
        if(my_C_socketfd!=-1)
        {
            pid=fork();
            if(pid==0)  //子进程
            {
                char file_buff[1024];
                char buff[1024];
                char* response_head="HTTP/1.1 200 OK\r\nContent-Type: application/octet-stream\r\n\r\n";
                int temp;

                // temp=recv(my_C_socketfd,buff,1024,0);                //保存信息到buff
                // printf("recv返回%d\n",temp);
                if(!recv(my_C_socketfd,buff,1024,0))
                {
                    close(my_C_socketfd);
                    close(my_listen_socketfd);
                    exit(0);
                }


                char *headline=strtok(buff,"\r\n");             //获得请求行
                char *url,*method,*file_url;
                method=strtok(headline," ");                    //获取请求方法
                url=strtok(NULL," ");                           //获取url
                // printf("helloa!\n");

                file_url=malloc(strlen(url)+7);                 
                file_url[0]='\0';
                strcat(file_url,"./data");
                strcat(file_url,url);                           //获取请求文件路径

                printf("\nmethod:%s;url:%s;file_url:%s\n",method,url,file_url); //验证程序执行

                // printf("hellob!\n");
                if(method&&file_url)
                {
                    if(!strcmp(method,"GET"))   //方法正确
                    {
                        FILE* thefile=fopen(file_url,"rb");

                        if(thefile)
                        {
                            printf("发回数据中...\n");
                            if(send(my_C_socketfd,response_head,strlen(response_head),0)<0)
                            {
                                fclose(thefile);
                                if(!close(my_C_socketfd)) printf("Close client_socket successfully!\n");
                                exit(0);
                            }
                            while (!feof(thefile))
                            {
                                fread(file_buff,1,1024,thefile);
                                if(send(my_C_socketfd,file_buff,1024,0)<0){
                                    printf("信号中断\n");
                                    break;
                                } 
                            }
                            fclose(thefile);
                            if(!close(my_C_socketfd)) printf("Close client_socket successfully!\n");
                        }
                        else    //文件错误
                        {
                            printf("文件错误");
                            send(my_C_socketfd,"HTTP/1.1 404 Not Found",22,0);
                            if(!close(my_C_socketfd)) printf("Close client_socket successfully!\n");
                        }
                    }
                    else    //非GET方法
                    {
                        if(!close(my_C_socketfd)) printf("Close client_socket successfully!\n");
                    }
                }                
                break;
            }
            else    //父进程
            {
                printf("accept successfully!sockid:%d forked pid:%d \n",my_C_socketfd,pid);
            }
        }
        close(my_C_socketfd);
    }
    printf("该进程结束\n");
    close(my_listen_socketfd);
    exit(0);
}