---
title: "Redis源码分析"
isCJKLanguage: true
date: 2021-11-28 20:35:41
updated: 2021-11-28 20:35:41
categories: 
- IT
- Redis
tags: 
- Redis
---

# Redis源码分析

[参考一: Redis源码分析](https://qiankunli.github.io/2019/04/20/redis_source.html)

[参考二: Redis主流程分析](http://zhangtielei.com/posts/blog-redis-how-to-start.html)

## Redis main函数



![image-20201008143758323](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201008143805.png)

## Redis主流程分析

每个成功建立的连接生成一个connection数据，connection数据结构定义: 

{%spoiler 示例代码%}
```
struct connection {
    ConnectionType *type;
    ConnectionState state;
    short int flags;
    short int refs;
    int last_errno;
    void *private_data;
    ConnectionCallbackFunc conn_handler;
    ConnectionCallbackFunc write_handler;
    ConnectionCallbackFunc read_handler;
    int fd;
};
```
{%endspoiler%}

{%spoiler 示例代码%}
```c
typedef struct ConnectionType {
    void (*ae_handler)(struct aeEventLoop *el, int fd, void *clientData, int mask);
    int (*connect)(struct connection *conn, const char *addr, int port, const char *source_addr, ConnectionCallbackFunc connect_handler);
    int (*write)(struct connection *conn, const void *data, size_t data_len);
    int (*read)(struct connection *conn, void *buf, size_t buf_len);
    void (*close)(struct connection *conn);
    int (*accept)(struct connection *conn, ConnectionCallbackFunc accept_handler);
    int (*set_write_handler)(struct connection *conn, ConnectionCallbackFunc handler, int barrier);
    int (*set_read_handler)(struct connection *conn, ConnectionCallbackFunc handler);
    const char *(*get_last_error)(struct connection *conn);
    int (*blocking_connect)(struct connection *conn, const char *addr, int port, long long timeout);
    ssize_t (*sync_write)(struct connection *conn, char *ptr, ssize_t size, long long timeout);
    ssize_t (*sync_read)(struct connection *conn, char *ptr, ssize_t size, long long timeout);
    ssize_t (*sync_readline)(struct connection *conn, char *ptr, ssize_t size, long long timeout);
} ConnectionType;
```
{%endspoiler%}

{%spoiler 示例代码%}
```
typedef enum {
    CONN_STATE_NONE = 0,
    CONN_STATE_CONNECTING,
    CONN_STATE_ACCEPTING,
    CONN_STATE_CONNECTED,
    CONN_STATE_CLOSED,
    CONN_STATE_ERROR
} ConnectionState;
```
{%endspoiler%}

其中type字段的初始值被设置为

{%spoiler 示例代码%}
```c
ConnectionType CT_Socket = {
    .ae_handler = connSocketEventHandler,
    .close = connSocketClose,
    .write = connSocketWrite,
    .read = connSocketRead,
    .accept = connSocketAccept,
    .connect = connSocketConnect,
    .set_write_handler = connSocketSetWriteHandler,
    .set_read_handler = connSocketSetReadHandler,
    .get_last_error = connSocketGetLastError,
    .blocking_connect = connSocketBlockingConnect,
    .sync_write = connSocketSyncWrite,
    .sync_read = connSocketSyncRead,
    .sync_readline = connSocketSyncReadLine
};
```
{%endspoiler%}

![Redis处理主流程及调用关系](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200920222038.png)