---
title: "Redis数据结构-dict"
isCJKLanguage: true
date: 2020-11-22 14:56:14
updated: 2020-11-22 14:56:14
categories: 
- IT
- Redis
tags: 
- Redis
---

# Redis数据结构--dict

关于dict的结构在src/dict.h，

dict:

{%spoiler 示例代码%}
```c
typedef struct dict {
    dictType *type;
    void *privdata;
    dictht ht[2];
    long rehashidx; /* rehashing not in progress if rehashidx == -1 */
    unsigned long iterators; /* number of iterators currently running */
} dict;
```
{%endspoiler%}

dictht:

{%spoiler 示例代码%}
```c
/* This is our hash table structure. Every dictionary has two of this as we
 * implement incremental rehashing, for the old to the new table. */
typedef struct dictht {
    dictEntry **table;
    unsigned long size;
    unsigned long sizemask;
    unsigned long used;
} dictht;
```
{%endspoiler%}

dictEntry:

{%spoiler 示例代码%}
```c
typedef struct dictEntry {
    void *key;
    union {
        void *val;
        uint64_t u64;
        int64_t s64;
        double d;
    } v;
    struct dictEntry *next;
} dictEntry;
```
{%endspoiler%}

dictType:

{%spoiler 示例代码%}
```c
typedef struct dictType {
    uint64_t (*hashFunction)(const void *key);
    void *(*keyDup)(void *privdata, const void *key);
    void *(*valDup)(void *privdata, const void *obj);
    int (*keyCompare)(void *privdata, const void *key1, const void *key2);
    void (*keyDestructor)(void *privdata, void *key);
    void (*valDestructor)(void *privdata, void *obj);
} dictType;
```
{%endspoiler%}