---
title: "socket中backlog的含义及影响"
isCJKLanguage: true
date: 2021-12-31 21:58:48
updated: "2022-01-02 17:53:33"
categories: 
- IT
- 网络
tags: 
- 网络
---

# socket中backlog的含义及影响

## 描述

先执行man listen看一下listen的原型：

{%spoiler 示例代码%}
```
NAME
       listen - listen for connections on a socket

SYNOPSIS
       #include <sys/types.h>          /* See NOTES */
       #include <sys/socket.h>

       int listen(int sockfd, int backlog);

DESCRIPTION
       listen() marks the socket referred to by sockfd as a passive socket, that is, as a socket that will be used to accept incoming connection requests using accept(2).

       The sockfd argument is a file descriptor that refers to a socket of type SOCK_STREAM or SOCK_SEQPACKET.

       The backlog argument defines the maximum length to which the queue of pending connections for sockfd may grow.  If a connection request arrives when the queue is full, the client may receive an error with an indication of ECON‐
       NREFUSED or, if the underlying protocol supports retransmission, the request may be ignored so that a later reattempt at connection succeeds.

RETURN VALUE
       On success, zero is returned.  On error, -1 is returned, and errno is set appropriately.
```
{%endspoiler%}

根据描述，backlog指定了该套接字上最大等待队列的长度。如果队列长度已满的话，会返回一个错误，或者是忽略连接请求（当下层协议支持重传的时候）。本文仅讨论Linux系统下、下层协议为TCP时的backlog含义。

**根据《Unix 网络编程：套接字联网API》（4.5 listen函数）（P84）章节的讨论，不同系统对于backlog有不同的解释。**

## 半连接队列和全连接队列

对应于TCP，Linux内核为每个监听套接字维护了两个队列：

* 半连接队列（SYN队列）：等待三次握手完成，处于SYN_RCVD状态的套接字；
* 全连接队列（Accept队列）：已完成三次握手，等待accept函数取出的套接字，处于Established状态。

## backlog参数

对于backlog参数的疑问主要是：

* 1、backlog指定的是哪个队列的长度，半连接队列？全连接队列？还是两个队列长度之和？
* 2、backlog与队列最大长度（假设为m）的关系？

* 3、队列长度达到backlog指定的最大长度时如何处理新请求？

  

继续查看listen相关的手册，可以看到：

{%spoiler 示例代码%}
```
The  behavior of the backlog argument on TCP sockets changed with Linux 2.2.  Now it specifies the queue length for completely established sockets waiting to be accepted, instead of the number of incomplete connection requests.
       The maximum length of the queue for incomplete sockets can be set using /proc/sys/net/ipv4/tcp_max_syn_backlog.  When syncookies are enabled there is no logical maximum length and this setting is ignored.  See tcp(7)  for  more
       information.

       If  the  backlog  argument  is  greater  than the value in /proc/sys/net/core/somaxconn, then it is silently truncated to that value; the default value in this file is 128.  In kernels before 2.4.25, this limit was a hard coded
       value, SOMAXCONN, with the value 128.
```
{%endspoiler%}

所以，对于以上三个问题的答案：

* 1、Linux 2.2版本之后，backlog指的是全连接队列的长度；

* 2、全连接队列最大长度是min(backlog, /proc/sys/net/core/somaxconn)，默认值是128。半连接队列最大长度则受/proc/sys/net/ipv4/tcp_max_syn_backlog和syncookies的控制；

  **测试后发现实际全连接队列最大长度是backlog+1**

  关于为什么是backlog+1的分析：

  > 从代码看，在将套接字转移到全连接队列前判断队列是否已满，而判断方法是sk->sk_ack_backlog > sk->sk_max_ack_backlog，所以队列长度达到backlog的时候判断会认为还没满，所以仍然可以添加新套接字到全连接队列里，直到队列长度达到backlog+1的时候才认为已满，不再建立新的连接。（需要进一步分析源码进行确认。参考[2]中也有人提出这个疑问。）

* 3、队列满的时候有两种处理方式：返回ECON‐
         NREFUSED，拒绝本次连接，或者忽略本次请求（需要下层协议支持重传）。所以对于TCP协议，处理方法应该是丢弃此次请求。另外会受到/proc/sys/net/ipv4/tcp_abort_on_overflow的控制：

  > 如果值为`0`, 服务端丢掉握手第三个ack包, 等同于认为客户端并没有回复 ack, 服务端重传 syn+ack 包. 如果值为`1`, 服务端直接回复 rst 包, 关闭连接.

## 实验验证

### backlog与队列长度/队列满的时候丢弃请求

#### 一、启动服务器程序，如图（参数表示的是backlog），backlog设置为1：

![image-20211224153424545](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20211224153431.png)

根据前文的描述，全连接队列里应该最多只有一个套接字，多余的连接请求应该会一直停在半连接队列里（半连接队列未满的情况下），直到全连接队列长度小于backlog。

#### 二、在另一个session使用ab发请求，设置并发量为4：

{%spoiler 示例代码%}
```shell
[root@VM-24-8-centos ~]# ab -n 4 -c 4 localhost:8088/
This is ApacheBench, Version 2.3 <$Revision: 1430300 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient).....done


Server Software:        NBS/1.0
Server Hostname:        localhost
Server Port:            8088

Document Path:          /
Document Length:        13 bytes

Concurrency Level:      4
Time taken for tests:   40.001 seconds
Complete requests:      4
Failed requests:        0
Write errors:           0
Total transferred:      520 bytes
HTML transferred:       52 bytes
Requests per second:    0.10 [#/sec] (mean)
Time per request:       40000.901 [ms] (mean)
Time per request:       10000.225 [ms] (mean, across all concurrent requests)
Transfer rate:          0.01 [Kbytes/sec] received

Connection Times (ms)
              min  mean[+/-sd] median   max
Connect:        0    0   0.0      0       0
Processing: 10000 25000 12910.1  30000   40001
Waiting:        0 15000 12910.1  20000   30000
Total:      10000 25000 12910.1  30001   40001

Percentage of the requests served within a certain time (ms)
  50%  30001
  66%  30001
  75%  40001
  80%  40001
  90%  40001
  95%  40001
  98%  40001
  99%  40001
 100%  40001 (longest request)
```
{%endspoiler%}

#### 三、查看套接字：

套接字情况如下（由于ab和服务器进程test在同一机器上，所以这里显示了两端的情况。分析时只需要关注第四列端口为8088的连接即可）。

可以看到一开始有三个连接状态为ESTABLISHED，另一个为SYN_RECV状态，一段时间后，才变为ESTABLISHED（实际是全连接队列中的套接字被accept处理了，所以这个套接字三次握手才成功建立，具体可参考服务端代码进行分析）。

这里可以看到，一开始ESTABLISHED状态的连接有三个，此时这三个连接中的情况为：

* 1）被服务进程（test）调用accept后处理中（最后一列显示有test），该套接字已从全连接队列中移除；
* 2）三次握手完成，在全连接队列中等待被accept取出处理（最后一列显示为-）；

显然，这里可以看出全连接队列最大长度是2，即backlog+1。

{%spoiler 示例代码%}
```shell
[root@VM-24-8-centos ~]# netstat -ntp|grep 8088
tcp        0      0 127.0.0.1:8088          127.0.0.1:59836         SYN_RECV    -                   
tcp        0      0 127.0.0.1:59834         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0     82 127.0.0.1:59836         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0      0 127.0.0.1:8088          127.0.0.1:59830         ESTABLISHED 5925/./test         
tcp        0      0 127.0.0.1:59830         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0      0 127.0.0.1:59832         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp       82      0 127.0.0.1:8088          127.0.0.1:59834         ESTABLISHED -                   
tcp       82      0 127.0.0.1:8088          127.0.0.1:59832         ESTABLISHED -                   
[root@VM-24-8-centos ~]# netstat -ntp|grep 8088
tcp        0      0 127.0.0.1:8088          127.0.0.1:59836         SYN_RECV    -                   
tcp        0      0 127.0.0.1:59834         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0     82 127.0.0.1:59836         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0      0 127.0.0.1:8088          127.0.0.1:59830         ESTABLISHED 5925/./test         
tcp        0      0 127.0.0.1:59830         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0      0 127.0.0.1:59832         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp       82      0 127.0.0.1:8088          127.0.0.1:59834         ESTABLISHED -                   
tcp       82      0 127.0.0.1:8088          127.0.0.1:59832         ESTABLISHED -                   
[root@VM-24-8-centos ~]# netstat -ntp|grep 8088
tcp        0      0 127.0.0.1:8088          127.0.0.1:59836         SYN_RECV    -                   
tcp        0      0 127.0.0.1:59834         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0     82 127.0.0.1:59836         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0      0 127.0.0.1:8088          127.0.0.1:59830         ESTABLISHED 5925/./test         
tcp        0      0 127.0.0.1:59830         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0      0 127.0.0.1:59832         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp       82      0 127.0.0.1:8088          127.0.0.1:59834         ESTABLISHED -                   
tcp       82      0 127.0.0.1:8088          127.0.0.1:59832         ESTABLISHED -                   
[root@VM-24-8-centos ~]# netstat -ntp|grep 8088
tcp        0      0 127.0.0.1:59836         127.0.0.1:8088          ESTABLISHED 6806/ab             
tcp        0      0 127.0.0.1:8088          127.0.0.1:59836         ESTABLISHED 5925/./test         
tcp        0      0 127.0.0.1:8088          127.0.0.1:59830         TIME_WAIT   -                   
tcp        0      0 127.0.0.1:8088          127.0.0.1:59834         TIME_WAIT   -                   
tcp        0      0 127.0.0.1:8088          127.0.0.1:59832         TIME_WAIT   -
```
{%endspoiler%}

#### 四、看一下抓包结果，并分析：

抓包结果如下。

在第三步查看套接字情况的时候可以看出，ab本次测试用的端口分别是59830、59832、59834、59836，与抓包结果相符合。进一步分析报文内容可以发现，对于前三个端口（59830、59832、59834），三次握手正常建立，这也基本与前一步看到的连接状况相符。唯独对于端口59836，服务器一直在重发SYN+ACK报文，从下文看，显然59836已经回复ACK，但是服务器进程并未处理这个ACK报文，反而一直在重发SYN+ACK报文，直到某一刻（基本是59830这个连接结束的时候，从服务端源码看，也正是accept从全连接队列中取出一个套接字的时候）。

{%spoiler 示例代码%}
```shell
[root@VM-24-8-centos ~]# tcpdump -nni any port 8088
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on any, link-type LINUX_SLL (Linux cooked), capture size 262144 bytes

20:50:51.727618 IP6 ::1.47368 > ::1.8088: Flags [S], seq 3876113499, win 43690, options [mss 65476,sackOK,TS val 2630303458 ecr 0,nop,wscale 7], length 0
20:50:51.727626 IP6 ::1.8088 > ::1.47368: Flags [R.], seq 0, ack 3876113500, win 0, length 0
20:50:51.727670 IP 127.0.0.1.59830 > 127.0.0.1.8088: Flags [S], seq 3925820849, win 43690, options [mss 65495,sackOK,TS val 2630303458 ecr 0,nop,wscale 7], length 0
20:50:51.727678 IP 127.0.0.1.8088 > 127.0.0.1.59830: Flags [S.], seq 3911357083, ack 3925820850, win 43690, options [mss 65495,sackOK,TS val 2630303458 ecr 2630303458,nop,wscale 7], length 0
20:50:51.727687 IP 127.0.0.1.59830 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 0
20:50:51.727704 IP 127.0.0.1.59830 > 127.0.0.1.8088: Flags [P.], seq 1:83, ack 1, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 82
20:50:51.727708 IP 127.0.0.1.8088 > 127.0.0.1.59830: Flags [.], ack 83, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 0
20:50:51.727785 IP 127.0.0.1.8088 > 127.0.0.1.59830: Flags [P.], seq 1:118, ack 83, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 117
20:50:51.727789 IP 127.0.0.1.59830 > 127.0.0.1.8088: Flags [.], ack 118, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 0
20:50:51.727795 IP 127.0.0.1.8088 > 127.0.0.1.59830: Flags [P.], seq 118:131, ack 83, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 13
20:50:51.727798 IP 127.0.0.1.59830 > 127.0.0.1.8088: Flags [.], ack 131, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 0
20:50:51.727842 IP 127.0.0.1.59832 > 127.0.0.1.8088: Flags [S], seq 288093760, win 43690, options [mss 65495,sackOK,TS val 2630303458 ecr 0,nop,wscale 7], length 0
20:50:51.727849 IP 127.0.0.1.8088 > 127.0.0.1.59832: Flags [S.], seq 1293060381, ack 288093761, win 43690, options [mss 65495,sackOK,TS val 2630303458 ecr 2630303458,nop,wscale 7], length 0
20:50:51.727855 IP 127.0.0.1.59832 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 0
20:50:51.727876 IP 127.0.0.1.59834 > 127.0.0.1.8088: Flags [S], seq 3380601055, win 43690, options [mss 65495,sackOK,TS val 2630303458 ecr 0,nop,wscale 7], length 0
20:50:51.727881 IP 127.0.0.1.8088 > 127.0.0.1.59834: Flags [S.], seq 1317065744, ack 3380601056, win 43690, options [mss 65495,sackOK,TS val 2630303458 ecr 2630303458,nop,wscale 7], length 0
20:50:51.727885 IP 127.0.0.1.59834 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 0
20:50:51.727900 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [S], seq 86886059, win 43690, options [mss 65495,sackOK,TS val 2630303458 ecr 0,nop,wscale 7], length 0
20:50:51.727922 IP 127.0.0.1.8088 > 127.0.0.1.59832: Flags [.], ack 83, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 0
20:50:51.727939 IP 127.0.0.1.8088 > 127.0.0.1.59834: Flags [.], ack 83, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 0
20:50:51.727946 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [P.], seq 86886060:86886142, ack 2883444459, win 342, options [nop,nop,TS val 2630303458 ecr 2630303458], length 82
20:50:51.927164 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [P.], seq 0:82, ack 1, win 342, options [nop,nop,TS val 2630303658 ecr 2630303458], length 82
20:50:52.127164 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [P.], seq 0:82, ack 1, win 342, options [nop,nop,TS val 2630303858 ecr 2630303458], length 82
20:50:52.528166 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [P.], seq 0:82, ack 1, win 342, options [nop,nop,TS val 2630304259 ecr 2630303458], length 82
20:50:52.929164 IP 127.0.0.1.8088 > 127.0.0.1.59836: Flags [S.], seq 2883444458, ack 86886060, win 43690, options [mss 65495,sackOK,TS val 2630304660 ecr 2630304259,nop,wscale 7], length 0
20:50:52.929175 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2630304660 ecr 2630303458], length 0
20:50:53.329163 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [P.], seq 1:83, ack 1, win 342, options [nop,nop,TS val 2630305060 ecr 2630303458], length 82
20:50:54.933162 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [P.], seq 1:83, ack 1, win 342, options [nop,nop,TS val 2630306664 ecr 2630303458], length 82
20:50:55.129167 IP 127.0.0.1.8088 > 127.0.0.1.59836: Flags [S.], seq 2883444458, ack 86886060, win 43690, options [mss 65495,sackOK,TS val 2630306860 ecr 2630306664,nop,wscale 7], length 0
20:50:55.129178 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2630306860 ecr 2630303458], length 0


20:50:58.141161 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [P.], seq 1:83, ack 1, win 342, options [nop,nop,TS val 2630309872 ecr 2630303458], length 82
20:50:59.329164 IP 127.0.0.1.8088 > 127.0.0.1.59836: Flags [S.], seq 2883444458, ack 86886060, win 43690, options [mss 65495,sackOK,TS val 2630311060 ecr 2630309872,nop,wscale 7], length 0
20:50:59.329176 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2630311060 ecr 2630303458], length 0
20:51:01.727911 IP 127.0.0.1.8088 > 127.0.0.1.59830: Flags [F.], seq 131, ack 83, win 342, options [nop,nop,TS val 2630313458 ecr 2630303458], length 0
20:51:01.727973 IP 127.0.0.1.8088 > 127.0.0.1.59832: Flags [P.], seq 1:118, ack 83, win 342, options [nop,nop,TS val 2630313458 ecr 2630303458], length 117
20:51:01.727979 IP 127.0.0.1.59832 > 127.0.0.1.8088: Flags [.], ack 118, win 342, options [nop,nop,TS val 2630313458 ecr 2630313458], length 0
20:51:01.727986 IP 127.0.0.1.8088 > 127.0.0.1.59832: Flags [P.], seq 118:131, ack 83, win 342, options [nop,nop,TS val 2630313458 ecr 2630313458], length 13
20:51:01.727990 IP 127.0.0.1.59832 > 127.0.0.1.8088: Flags [.], ack 131, win 342, options [nop,nop,TS val 2630313458 ecr 2630313458], length 0
20:51:01.728022 IP 127.0.0.1.59830 > 127.0.0.1.8088: Flags [F.], seq 83, ack 132, win 342, options [nop,nop,TS val 2630313458 ecr 2630313458], length 0
20:51:01.728029 IP 127.0.0.1.8088 > 127.0.0.1.59830: Flags [.], ack 84, win 342, options [nop,nop,TS val 2630313458 ecr 2630313458], length 0
20:51:04.557166 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [P.], seq 1:83, ack 1, win 342, options [nop,nop,TS val 2630316288 ecr 2630303458], length 82
20:51:04.557185 IP 127.0.0.1.8088 > 127.0.0.1.59836: Flags [.], ack 83, win 342, options [nop,nop,TS val 2630316288 ecr 2630316288], length 0
20:51:11.728090 IP 127.0.0.1.8088 > 127.0.0.1.59832: Flags [F.], seq 131, ack 83, win 342, options [nop,nop,TS val 2630323458 ecr 2630313458], length 0
20:51:11.728172 IP 127.0.0.1.8088 > 127.0.0.1.59834: Flags [P.], seq 1:118, ack 83, win 342, options [nop,nop,TS val 2630323459 ecr 2630303458], length 117
20:51:11.728179 IP 127.0.0.1.59834 > 127.0.0.1.8088: Flags [.], ack 118, win 342, options [nop,nop,TS val 2630323459 ecr 2630323459], length 0
20:51:11.728186 IP 127.0.0.1.8088 > 127.0.0.1.59834: Flags [P.], seq 118:131, ack 83, win 342, options [nop,nop,TS val 2630323459 ecr 2630323459], length 13
20:51:11.728189 IP 127.0.0.1.59834 > 127.0.0.1.8088: Flags [.], ack 131, win 342, options [nop,nop,TS val 2630323459 ecr 2630323459], length 0
20:51:11.728218 IP 127.0.0.1.59832 > 127.0.0.1.8088: Flags [F.], seq 83, ack 132, win 342, options [nop,nop,TS val 2630323459 ecr 2630323458], length 0
20:51:11.728225 IP 127.0.0.1.8088 > 127.0.0.1.59832: Flags [.], ack 84, win 342, options [nop,nop,TS val 2630323459 ecr 2630323459], length 0
20:51:21.728295 IP 127.0.0.1.8088 > 127.0.0.1.59834: Flags [F.], seq 131, ack 83, win 342, options [nop,nop,TS val 2630333459 ecr 2630323459], length 0
20:51:21.728360 IP 127.0.0.1.8088 > 127.0.0.1.59836: Flags [P.], seq 1:118, ack 83, win 342, options [nop,nop,TS val 2630333459 ecr 2630316288], length 117
20:51:21.728369 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [.], ack 118, win 342, options [nop,nop,TS val 2630333459 ecr 2630333459], length 0
20:51:21.728377 IP 127.0.0.1.8088 > 127.0.0.1.59836: Flags [P.], seq 118:131, ack 83, win 342, options [nop,nop,TS val 2630333459 ecr 2630333459], length 13
20:51:21.728381 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [.], ack 131, win 342, options [nop,nop,TS val 2630333459 ecr 2630333459], length 0
20:51:21.728407 IP 127.0.0.1.59834 > 127.0.0.1.8088: Flags [F.], seq 83, ack 132, win 342, options [nop,nop,TS val 2630333459 ecr 2630333459], length 0
20:51:21.728413 IP 127.0.0.1.8088 > 127.0.0.1.59834: Flags [.], ack 84, win 342, options [nop,nop,TS val 2630333459 ecr 2630333459], length 0
20:51:31.728440 IP 127.0.0.1.8088 > 127.0.0.1.59836: Flags [F.], seq 131, ack 83, win 342, options [nop,nop,TS val 2630343459 ecr 2630333459], length 0
20:51:31.728503 IP 127.0.0.1.59836 > 127.0.0.1.8088: Flags [F.], seq 83, ack 132, win 342, options [nop,nop,TS val 2630343459 ecr 2630343459], length 0
20:51:31.728512 IP 127.0.0.1.8088 > 127.0.0.1.59836: Flags [.], ack 84, win 342, options [nop,nop,TS val 2630343459 ecr 2630343459], length 0
```
{%endspoiler%}

#### 五、/proc/sys/net/ipv4/tcp_abort_on_overflow设置为1，观察抓包结果：

显然这次使用的是33536、33538、33540、33542四个端口，看一下抓包结果，明显对于端口33542，在三次握手的报文之后，服务器进程直接发送了一个RST报文。

{%spoiler 示例代码%}
```
[root@VM-24-8-centos ~]# ab -n 4 -c 4 localhost:8088/
This is ApacheBench, Version 2.3 <$Revision: 1430300 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)...apr_socket_recv: Connection reset by peer (104)
[root@VM-24-8-centos ~]# ^C
[root@VM-24-8-centos ~]# ab -n 4 -c 4 localhost:8088/
This is ApacheBench, Version 2.3 <$Revision: 1430300 $>
Copyright 1996 Adam Twiss, Zeus Technology Ltd, http://www.zeustech.net/
Licensed to The Apache Software Foundation, http://www.apache.org/

Benchmarking localhost (be patient)...apr_socket_recv: Connection reset by peer (104)
```
{%endspoiler%}



{%spoiler 示例代码%}
```shell
[root@VM-24-8-centos ~]# netstat -ntp|grep 8088
tcp        0      0 127.0.0.1:33538         127.0.0.1:8088          FIN_WAIT2   -                   
tcp        0      0 127.0.0.1:33540         127.0.0.1:8088          FIN_WAIT2   -                   
tcp       83      0 127.0.0.1:8088          127.0.0.1:33538         CLOSE_WAIT  -                   
tcp        0      0 127.0.0.1:33536         127.0.0.1:8088          FIN_WAIT2   -                   
tcp        1      0 127.0.0.1:8088          127.0.0.1:33536         CLOSE_WAIT  14918/./test        
tcp       83      0 127.0.0.1:8088          127.0.0.1:33540         CLOSE_WAIT  -
```
{%endspoiler%}



{%spoiler 示例代码%}
```shell
[root@VM-24-8-centos ~]# tcpdump -nni any port 8088
tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
listening on any, link-type LINUX_SLL (Linux cooked), capture size 262144 bytes


21:24:51.241971 IP6 ::1.49306 > ::1.8088: Flags [S], seq 537212558, win 43690, options [mss 65476,sackOK,TS val 2632342972 ecr 0,nop,wscale 7], length 0
21:24:51.241979 IP6 ::1.8088 > ::1.49306: Flags [R.], seq 0, ack 537212559, win 0, length 0
21:24:51.242023 IP 127.0.0.1.33536 > 127.0.0.1.8088: Flags [S], seq 2771398844, win 43690, options [mss 65495,sackOK,TS val 2632342972 ecr 0,nop,wscale 7], length 0
21:24:51.242031 IP 127.0.0.1.8088 > 127.0.0.1.33536: Flags [S.], seq 214599834, ack 2771398845, win 43690, options [mss 65495,sackOK,TS val 2632342972 ecr 2632342972,nop,wscale 7], length 0
21:24:51.242038 IP 127.0.0.1.33536 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2632342972 ecr 2632342972], length 0
21:24:51.242054 IP 127.0.0.1.33536 > 127.0.0.1.8088: Flags [P.], seq 1:83, ack 1, win 342, options [nop,nop,TS val 2632342972 ecr 2632342972], length 82
21:24:51.242058 IP 127.0.0.1.8088 > 127.0.0.1.33536: Flags [.], ack 83, win 342, options [nop,nop,TS val 2632342972 ecr 2632342972], length 0
21:24:51.242169 IP 127.0.0.1.8088 > 127.0.0.1.33536: Flags [P.], seq 1:118, ack 83, win 342, options [nop,nop,TS val 2632342973 ecr 2632342972], length 117
21:24:51.242173 IP 127.0.0.1.33536 > 127.0.0.1.8088: Flags [.], ack 118, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242179 IP 127.0.0.1.8088 > 127.0.0.1.33536: Flags [P.], seq 118:131, ack 83, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 13
21:24:51.242182 IP 127.0.0.1.33536 > 127.0.0.1.8088: Flags [.], ack 131, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242214 IP 127.0.0.1.33538 > 127.0.0.1.8088: Flags [S], seq 2527639607, win 43690, options [mss 65495,sackOK,TS val 2632342973 ecr 0,nop,wscale 7], length 0
21:24:51.242218 IP 127.0.0.1.8088 > 127.0.0.1.33538: Flags [S.], seq 3509174586, ack 2527639608, win 43690, options [mss 65495,sackOK,TS val 2632342973 ecr 2632342973,nop,wscale 7], length 0
21:24:51.242224 IP 127.0.0.1.33538 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242247 IP 127.0.0.1.33540 > 127.0.0.1.8088: Flags [S], seq 3237997584, win 43690, options [mss 65495,sackOK,TS val 2632342973 ecr 0,nop,wscale 7], length 0
21:24:51.242254 IP 127.0.0.1.8088 > 127.0.0.1.33540: Flags [S.], seq 3084261840, ack 3237997585, win 43690, options [mss 65495,sackOK,TS val 2632342973 ecr 2632342973,nop,wscale 7], length 0
21:24:51.242261 IP 127.0.0.1.33540 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242281 IP 127.0.0.1.33542 > 127.0.0.1.8088: Flags [S], seq 3051525301, win 43690, options [mss 65495,sackOK,TS val 2632342973 ecr 0,nop,wscale 7], length 0
21:24:51.242286 IP 127.0.0.1.8088 > 127.0.0.1.33542: Flags [S.], seq 2696146235, ack 3051525302, win 43690, options [mss 65495,sackOK,TS val 2632342973 ecr 2632342973,nop,wscale 7], length 0
21:24:51.242290 IP 127.0.0.1.33542 > 127.0.0.1.8088: Flags [.], ack 1, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242295 IP 127.0.0.1.8088 > 127.0.0.1.33542: Flags [R], seq 2696146236, win 0, length 0
21:24:51.242309 IP 127.0.0.1.33538 > 127.0.0.1.8088: Flags [P.], seq 1:83, ack 1, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 82
21:24:51.242311 IP 127.0.0.1.8088 > 127.0.0.1.33538: Flags [.], ack 83, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242318 IP 127.0.0.1.33540 > 127.0.0.1.8088: Flags [P.], seq 1:83, ack 1, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 82
21:24:51.242321 IP 127.0.0.1.8088 > 127.0.0.1.33540: Flags [.], ack 83, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242346 IP 127.0.0.1.33540 > 127.0.0.1.8088: Flags [F.], seq 83, ack 1, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242352 IP 127.0.0.1.33538 > 127.0.0.1.8088: Flags [F.], seq 83, ack 1, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.242357 IP 127.0.0.1.33536 > 127.0.0.1.8088: Flags [F.], seq 83, ack 131, win 342, options [nop,nop,TS val 2632342973 ecr 2632342973], length 0
21:24:51.282157 IP 127.0.0.1.8088 > 127.0.0.1.33536: Flags [.], ack 84, win 342, options [nop,nop,TS val 2632343013 ecr 2632342973], length 0
21:24:51.282160 IP 127.0.0.1.8088 > 127.0.0.1.33538: Flags [.], ack 84, win 342, options [nop,nop,TS val 2632343013 ecr 2632342973], length 0
21:24:51.282161 IP 127.0.0.1.8088 > 127.0.0.1.33540: Flags [.], ack 84, win 342, options [nop,nop,TS val 2632343013 ecr 2632342973], length 0
```
{%endspoiler%}

## 测试服务器源码

{%spoiler 示例代码%}
```c
#include <sys/select.h>  
#include <sys/time.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <arpa/inet.h>

#include <stdio.h>
#include <stdlib.h>
#include <string.h>


/* 请求头信息 */
typedef struct{
	char uri[256];			//uri
	char method[16];		//请求方法
	char version[16];		//版本
	char filename[256];		//文件名(包含完整路径)
	char name[256];			//文件名(不包含完整路径)
	char queryArgs[256];	//查询参数
	char contentType[256];		//请求体类型
	char contentLen[16];	//请求体长度
}http_header_t, hhr_t;


/* 响应头信息 */
typedef struct{
	char version[16];
	int statusCode;
	char msg[16];
	char server[32];
	char acceptRange[16];
	char connection[16];
	char contentType[32];
	int contentLen;
}response_header_t, rhr_t;


/** 
 * 创建SOCKET
 */
int create_socket()
{
	struct sockaddr_in server_addr;
	
	int socket_server = socket(AF_INET, SOCK_STREAM, 0);
	if (socket_server < 0)
	{
		printf("Socket Create Error!");
		exit(-1);
	}
	
	return socket_server;
}


/** 
 * 绑定地址和端口
 */
int bind_address(int sockfd)
{
	int server_port = 8088;
	
	struct sockaddr_in server_addr;
	server_addr.sin_family = AF_INET;
	server_addr.sin_port = htons(server_port);
	server_addr.sin_addr.s_addr = INADDR_ANY;
	
	if( bind(sockfd, &server_addr, sizeof(server_addr)) == -1 )
	{
		printf("Bind Error!");
		exit(-1);
	}
	
	return 0;
}


/** 
 * 启动服务器，绑定监听地址和端口，开始监听
 */
int start_server(int backlog)
{
	int socket_server = create_socket();
	bind_address(socket_server);
	listen(socket_server, backlog);
	
	return socket_server;
}


/** 
 * 等待客户请求
 */
int wait_request(int sockfd)
{
	printf("Waitting connect...\n");
	struct sockaddr_in client_addr;
	int addr_len = sizeof(client_addr);
	
	int socket_client = accept(sockfd, &client_addr, &addr_len);
	if(socket_client == -1)
		return -1;

	printf("Client address:%s, port: %d.\n", inet_ntoa(client_addr.sin_addr), ntohs(client_addr.sin_port));
	return socket_client;
}


/** 
 * 读取一行
 *
 * @param const SOCKET socketClient 
 * @param char *buf 
 * @param int maxLine 每行的最大字符数
 *
 * @return int 读取进buf中的字符数
 */
int read_line(const int socketClient, char *buf, int maxLine)
{
	int i = 0;
	while ((recv(socketClient, buf+i, 1, 0) > 0) && (i < maxLine))
	{
		if (*(buf+i) == 10 )
		{
			*(buf+i-1) = 0; //清除读到的'\r\n'字符
			i = i - 2;
			break;
		}
		i++;
	}
	//printf("%s\n", requestLine);
	return i; //读取到的'\r\n'被丢弃,所以-2
}


void server(int sockfd)
{
    /* 读取请求行 */
    char *requestLine = (char*)calloc(300, sizeof(char));
    read_line(sockfd, requestLine, 300);
    printf("%s\n", requestLine);

    free(requestLine);
    requestLine = NULL;

    /* 读取出全部数据 */
    char *requestHead = (char*)calloc(300, sizeof(char));
    int i = 0;
    int n = 0;
    while ( (n=recv(sockfd, requestHead, 300, MSG_DONTWAIT)) > 0 )
    {
        printf("%s\n", requestHead);
    }
    free(requestHead);
    requestHead = NULL;

    char *buf = "Hello World!\n";
    rhr_t *rhr = (rhr_t*)calloc(1, sizeof(rhr_t));
    /* 响应头信息 */
	strcpy(rhr->version, "HTTP/1.1");
	rhr->statusCode = 200;
	strcpy(rhr->msg, "success");
	strcpy(rhr->server, "TBS/1.0");
	strcpy(rhr->acceptRange, "bytes");
	strcpy(rhr->connection, "close");
    rhr->contentLen = strlen(buf);

    char *responseHead = (char*)calloc(1024, 1);
    sprintf(responseHead, "%s %d %s\r\n", rhr->version, rhr->statusCode, rhr->msg); //"HTTP/1.0 200 OK\r\n");
    sprintf(responseHead, "%sServer: %s\r\n", responseHead, rhr->server);
	sprintf(responseHead, "%sAccept-range: %s\r\n", responseHead, rhr->acceptRange);
    sprintf(responseHead, "%sConnection: %s\r\n", responseHead, rhr->connection);
	sprintf(responseHead, "%sContent-type: %s\r\n", responseHead, rhr->contentType);
	sprintf(responseHead, "%sContent-length: %d\r\n", responseHead, rhr->contentLen);	
	sprintf(responseHead, "%s\r\n", responseHead);

    printf("%d\n", strlen(responseHead));
    write(sockfd, responseHead, strlen(responseHead));
    write(sockfd, buf, strlen(buf));

    free(rhr);
    free(responseHead);
    rhr = NULL;
    responseHead = NULL;
}


int main(int argc, char *argv[])
{
	/* 启动服务器，绑定监听地址和端口 */
    int backlog = atoi(argv[1]);
	int socket_server = start_server(backlog);
	printf("START SERVER AT 127.0.0.1:%d, backlog: %d.\n", 8088, backlog);

    //struct linger so_linger;
    //so_linger.l_onoff = 1;
    //so_linger.l_linger = 0;
    //setsockopt(socket_server, SOL_SOCKET, SO_LINGER, &so_linger, sizeof so_linger);
        
	while(1)
	{
		//printf("---------------------------------------------\n");
		int socket_client = wait_request(socket_server);
		if(socket_client == -1)
		{
			//printf("Connect Error!");
			continue;
		}
		
		/* 处理客户端请求 */
		server(socket_client);
        sleep(10);
        printf("关闭本连接...\n");
        close(socket_client);
	}
	
	/* 关闭服务器 */
	close(socket_server);
	return 0;
}
```
{%endspoiler%}



## 参考

[[1] TCP 半连接队列和全连接队列](https://blog.isayme.org/posts/issues-47/)

[[2] TCP 的backlog详解及半连接队列和全连接队列](https://blog.csdn.net/u010039418/article/details/78369343)

[[3] Unix 网络编程 卷1：套接字联网API](https://blog.csdn.net/u010039418/article/details/78369343)