---
title: "可重入函数、可重入锁与threading.Condition"
isCJKLanguage: true
date: 2021-11-28 20:35:42
updated: 2021-11-28 20:35:42
categories: 
- 编程
- 并发编程
tags: 
- 并发
---

# 可重入函数、可重入锁与threading.Condition

## 一、可重入函数与可重入锁

### 1、可重入函数

可在执行的任何时刻被中断然后调度程序执行另一段代码，这段代码再次调用该子程序而不出错。

官方定义:

{%spoiler 示例代码%}
```
A computer program or routine is described as reentrant if it can be safely called again before its previous invocation has been completed (i.e it can be safely executed concurrently)
```
{%endspoiler%}

**可重入函数的条件**:

* 不能使用全局变量或者引用外部地址。函数内可能修改这些变量。
* 可重入函数的代码应该保持一致。避免使用可重入函数的副本(???)。

* 不能使用非可重入锁。非可重入锁会导致阻塞(被中断的子例程可能持有该锁而未释放)。

  

**可重入函数与线程安全**:

本质区别: 可重入函数是单线程时代出现的概念，与多线程无关。

函数可能是线程安全但不可重入，比如，使用了互斥锁。



### 2、可重入锁

同一线程获得锁之后，该线程内部仍能再次获得该锁。



## threading.Condition

{%spoiler 示例代码%}
```
pass
```
{%endspoiler%}



[参考一: 可重入函数与可重入锁](https://segmentfault.com/a/1190000022571212)

[参考二: Reentrant Function](https://www.geeksforgeeks.org/reentrant-function/)

[参考三: RLock源码分析](https://reishin.me/python-source-code-parse-with-rlock/)

[参考四: threading.Condition源码分析](http://timd.cn/python/threading/condition/)