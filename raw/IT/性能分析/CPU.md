# 性能分析-CPU

## 性能指标

### 负载

负载反应了一定时间内活跃进程的数量。具体说是，一段时间内，处于可运行状态或不可中断状态的进程数量。贴一段man uptime原文:

> System load averages is the average number of processes that are either in a runnable or uninterruptable state.  A process in a runnable state is  either
>        using the CPU or waiting to use the CPU.  A process in uninterruptable state is waiting for some I/O access, eg waiting for disk.  The averages are taken
>        over the three time intervals.  Load averages are not normalized for the number of CPUs in a system, so a load average of 1 means a single CPU system  is
>        loaded all the time while on a 4 CPU system it means it was idle 75% of the time.

一般而言，负载大于逻辑核数时就说明出现过载了，但具体情况还要结合一段时间内的负载情况来进行分析。

### 使用率

使用率反映了CPU时间的分配情况。



## 参考

[参考一: Linux Load Averages：什么是平均负载？](https://zhuanlan.zhihu.com/p/75975041)

[参考二: Linux Load Averages: Solving the Mystery](http://www.brendangregg.com/blog/2017-08-08/linux-load-averages.html)

[参考三: 理解 %IOWAIT (%WIO)](http://linuxperf.com/?p=33)