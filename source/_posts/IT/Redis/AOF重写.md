---
title: "AOF重写"
isCJKLanguage: true
date: 2021-11-28 20:35:41
updated: 2021-11-28 20:35:41
categories: 
- IT
- Redis
tags: 
- Redis
---

# AOF

**note: 本文参考代码基于Redis 6.0**

## AOF写入

### 配置项

* appendonly：yes/no，是否开启AOF

* appendfsync：everysec/always/no

  AOF日志刷盘时机：每秒刷盘/每次写入立即刷盘/有操作系统控制

* no-appendfsync-on-rewrite：yes/no

  RDB生成或者AOF重写期间是否阻止主进程调用fsync

* AOF重写的控制条件：

  * auto-aof-rewrite-percentage 100
  * auto-aof-rewrite-min-size 64mb

* aof-load-truncated: yes/no, AOF日志不完整时的处置方式

* aof-use-rdb-preamble： yes/no，是否开启RDB/AOF混合持久化

### AOF缓冲区写入过程

redisServer中定义了一个aof写入缓冲区：

{%spoiler 示例代码%}
```c
sds aof_buf;      /* AOF buffer, written before entering the event loop */
```
{%endspoiler%}

每次执行写命令时会将命令追加到这个缓冲区，调用链：

![AOF缓冲区写入过程](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210509174559.png)

### AOF文件写入

AOF文件写入的时机：

* 每次写命令执行时，该命令已经被写入AOF缓冲区，在beforeSleep（该函数会在主进程进入事件循环等待前被调用）中会将缓冲区内容写入文件（不一定会刷盘）；
* 如果写入AOF时发现有sync在处理中，或者上次AOF写入有错误，则会在serverCron中执行AOF文件写操作；
* 主进程或者文件描述符关闭前执行写入。

## AOF重写

### AOF重写的触发条件

src/server.c line 1845, server_cron函数中，周期性检查是否满足AOF重写条件：

代码片段一：

{%spoiler 示例代码%}
```c
/* Trigger an AOF rewrite if needed. */
        if (server.aof_state == AOF_ON &&
            !hasActiveChildProcess() &&
            server.aof_rewrite_perc &&
            server.aof_current_size > server.aof_rewrite_min_size)
        {
            long long base = server.aof_rewrite_base_size ?
                server.aof_rewrite_base_size : 1;
            long long growth = (server.aof_current_size*100/base) - 100;
            if (growth >= server.aof_rewrite_perc) {
                serverLog(LL_NOTICE,"Starting automatic rewriting of AOF on %lld%% growth",growth);
                rewriteAppendOnlyFileBackground();
            }
        }
```
{%endspoiler%}

代码片段二:

{%spoiler 示例代码%}
```c
/* Start a scheduled AOF rewrite if this was requested by the user while
     * a BGSAVE was in progress. */
    if (!hasActiveChildProcess() &&
        server.aof_rewrite_scheduled)
    {
        rewriteAppendOnlyFileBackground();
    }
```
{%endspoiler%}

根据上面两个片段，总结重写条件为:

* AOF被激活；

* 没有活跃的子进程（未进行RDB保存、AOF重写，或某些加载模块产生的子进程?）；
* 当前aof文件大于auto-aof-rewrite-min-size（默认64MB）；
* 上次重写AOF文件以来，文件大小增长大于auto-aof-rewrite-percentage（默认100%）;

### AOF 重写缓冲区

#### AOF重写缓冲区相关的数据结构

{%spoiler 示例代码%}
```c
#define AOF_RW_BUF_BLOCK_SIZE (1024*1024*10)    /* 10 MB per block */

typedef struct aofrwblock {
    unsigned long used, free;
    char buf[AOF_RW_BUF_BLOCK_SIZE];
} aofrwblock;
```
{%endspoiler%}

server.h redisServer中定义了重写缓冲区：

{%spoiler 示例代码%}
```c
list *aof_rewrite_buf_blocks;   /* Hold changes during an AOF rewrite. */
```
{%endspoiler%}

#### 重写缓冲区大小限制

重写缓冲区是个链表，无大小限制。内存达到max-memory后会触发内存淘汰策略。

#### 重写缓冲区写入操作

aof.c line 184, feedAppendOnlyFile:

{%spoiler 示例代码%}
```c
...
/* If a background append only file rewriting is in progress we want to
     * accumulate the differences between the child DB and the current one
     * in a buffer, so that when the child process will do its work we
     * can append the differences to the new append only file. */
    if (server.aof_child_pid != -1)
        aofRewriteBufferAppend((unsigned char*)buf,sdslen(buf));
        ...
```
{%endspoiler%}

aof.c line 95, aofRewriteBufferAppend:

{%spoiler 示例代码%}
```c
/* Append data to the AOF rewrite buffer, allocating new blocks if needed. */
void aofRewriteBufferAppend(unsigned char *s, unsigned long len) {
    listNode *ln = listLast(server.aof_rewrite_buf_blocks);
    aofrwblock *block = ln ? ln->value : NULL;

    while(len) {
        /* If we already got at least an allocated block, try appending
         * at least some piece into it. */
        if (block) {
            unsigned long thislen = (block->free < len) ? block->free : len;
            if (thislen) {  /* The current block is not already full. */
                memcpy(block->buf+block->used, s, thislen);
                block->used += thislen;
                block->free -= thislen;
                s += thislen;
                len -= thislen;
            }
        }

        if (len) { /* First block to allocate, or need another block. */
            int numblocks;

            block = zmalloc(sizeof(*block));
            block->free = AOF_RW_BUF_BLOCK_SIZE;
            block->used = 0;
            listAddNodeTail(server.aof_rewrite_buf_blocks,block);

            /* Log every time we cross more 10 or 100 blocks, respectively
             * as a notice or warning. */
            numblocks = listLength(server.aof_rewrite_buf_blocks);
            if (((numblocks+1) % 10) == 0) {
                int level = ((numblocks+1) % 100) == 0 ? LL_WARNING :
                                                         LL_NOTICE;
                serverLog(level,"Background AOF buffer size: %lu MB",
                    aofRewriteBufferSize()/(1024*1024));
            }
        }
    }

    /* Install a file event to send data to the rewrite child if there is
     * not one already. */
    if (aeGetFileEvents(server.el,server.aof_pipe_write_data_to_child) == 0) {
        aeCreateFileEvent(server.el, server.aof_pipe_write_data_to_child,
            AE_WRITABLE, aofChildWriteDiffData, NULL);
    }
}
```
{%endspoiler%}

aof.c line 95, aofChildWriteDiffDatah：

{%spoiler 示例代码%}
```c
/* Event handler used to send data to the child process doing the AOF
 * rewrite. We send pieces of our AOF differences buffer so that the final
 * write when the child finishes the rewrite will be small. */
void aofChildWriteDiffData(aeEventLoop *el, int fd, void *privdata, int mask) {
    listNode *ln;
    aofrwblock *block;
    ssize_t nwritten;
    UNUSED(el);
    UNUSED(fd);
    UNUSED(privdata);
    UNUSED(mask);

    while(1) {
        ln = listFirst(server.aof_rewrite_buf_blocks);
        block = ln ? ln->value : NULL;
        if (server.aof_stop_sending_diff || !block) {
            aeDeleteFileEvent(server.el,server.aof_pipe_write_data_to_child,
                              AE_WRITABLE);
            return;
        }
        if (block->used > 0) {
            nwritten = write(server.aof_pipe_write_data_to_child,
                             block->buf,block->used);
            if (nwritten <= 0) return;
            memmove(block->buf,block->buf+nwritten,block->used-nwritten);
            block->used -= nwritten;
            block->free += nwritten;
        }
        if (block->used == 0) listDelNode(server.aof_rewrite_buf_blocks,ln);
    }
}
```
{%endspoiler%}

AOF重写期间，主进程会复制AOF重写缓冲区（aof_rewrite_buf_blocks）的内容到aof_pipe_write_data_to_child，aof_pipe_write_data_to_child实际是一个pipe，用于父子进程通信。子进程会从pipe取数据追加到新生成的AOF文件。

## 参考

[参考一: Redis之AOF重写及其实现原理](https://blog.csdn.net/hezhiqiang1314/article/details/69396887)