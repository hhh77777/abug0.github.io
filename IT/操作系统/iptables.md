# iptables

## 目录

[TOC]

### 参考

[参考一: iptables基本知识](https://kuring.me/post/iptables/)

### 概念：chain、table、rule

![iptables1](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200817195020.png)

![iptables2](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200817195832.png)

#### chain

PREROUTNG:报文到达本机，路由决策之前

INPUT:报文到达本机，向协议栈上层传递

OUTPUT:报文从本机发出，路由决策之前

POSTROUTING：报文从本机发出，路由决策之后

FORWARD:经由本机转发

#### table

对rule进行管理，存放相同功能的rule

filter:默认表，实现包过滤

nat:对包进行NAT

mangle:修改报文并封装

raw:标记数据包

#### rule

包含匹配条件和处理动作

source ip、destination ip、source port、destination port

accept、drop、reject、queue、dnat、snat、masquerade







