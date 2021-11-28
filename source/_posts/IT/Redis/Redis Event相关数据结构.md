---
title: "Redis Event相关数据结构"
isCJKLanguage: true
date: 2020-10-08 14:59:12
updated: 2020-10-08 14:59:12
categories: 
- IT
- Redis
tags: 
- Redis
---

# Redis Event数据结构

**声明文件：ae.h**

{%spoiler 示例代码%}
```c
/* State of an event based program */
typedef struct aeEventLoop {
    int maxfd;   /* highest file descriptor currently registered */
    int setsize; /* max number of file descriptors tracked */
    long long timeEventNextId;
    time_t lastTime;     /* Used to detect system clock skew */
    aeFileEvent *events; /* Registered events */
    aeFiredEvent *fired; /* Fired events */
    aeTimeEvent *timeEventHead;
    int stop;
    void *apidata; /* This is used for polling API specific data */
    aeBeforeSleepProc *beforesleep;
    aeBeforeSleepProc *aftersleep;
    int flags;
} aeEventLoop;
```
{%endspoiler%}



{%spoiler 示例代码%}
```c
typedef struct aeFileEvent {
    int mask; /* one of AE_(READABLE|WRITABLE|BARRIER) */
    aeFileProc *rfileProc;
    aeFileProc *wfileProc;
    void *clientData;
} aeFileEvent;
```
{%endspoiler%}

{%spoiler 示例代码%}
```c
/* Time event structure */
typedef struct aeTimeEvent {
    long long id; /* time event identifier. */
    long when_sec; /* seconds */
    long when_ms; /* milliseconds */
    aeTimeProc *timeProc;
    aeEventFinalizerProc *finalizerProc;
    void *clientData;
    struct aeTimeEvent *prev;
    struct aeTimeEvent *next;
    int refcount; /* refcount to prevent timer events from being
  		   * freed in recursive time event calls. */
} aeTimeEvent;
```
{%endspoiler%}

{%spoiler 示例代码%}
```c
/* A fired event */
typedef struct aeFiredEvent {
    int fd;
    int mask;
} aeFiredEvent;
```
{%endspoiler%}

{%spoiler 示例代码%}
```c
typedef struct aeApiState {
    int epfd;
    struct epoll_event *events;
} aeApiState;
```
{%endspoiler%}