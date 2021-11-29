---
title: "Using where与ICP"
isCJKLanguage: true
date: 2021-11-28 20:35:41
updated: 2021-11-28 20:35:41
categories: 
- IT
- MySQL
tags: 
- MySQL
---

# MySQL-Using where与ICP

## 介绍

引用自官网：

> - `Using index condition` (JSON property: `using_index_condition`)
>
>   Tables are read by accessing index tuples and testing them first to determine whether to read full table rows. In this way, index information is used to defer (“push down”) reading full table rows unless it is necessary. See [Section 8.2.1.6, “Index Condition Pushdown Optimization”](https://dev.mysql.com/doc/refman/8.0/en/index-condition-pushdown-optimization.html).
>
> - A `WHERE` clause is used to restrict which rows to match against the next table or send to the client. Unless you specifically intend to fetch or examine all rows from the table, you may have something wrong in your query if the `Extra` value is not `Using where` and the table join type is [`ALL`](https://dev.mysql.com/doc/refman/8.0/en/explain-output.html#jointype_all) or [`index`](https://dev.mysql.com/doc/refman/8.0/en/explain-output.html#jointype_index).
>
>   `Using where` has no direct counterpart in JSON-formatted output; the `attached_condition` property contains any `WHERE` condition used.

Using index condition表示使用了ICP。ICP(Index Condition push)是MySQL5.6引入的一项优化，是将where条件中可以使用索引字段的部分条件下放到存储引擎层，由引擎层在访问索引时进行过滤，这样可以减少回表次数以及引擎层与MySQL服务器间的交互数据量。

Using where用于限制需要发送的结果集。

## 问题

* Using where是否表示引擎层取数据后在服务层根据where做了过滤？
* 仅根据索引过滤时是否会显示Using where？

## 出现的场景

建表

{%spoiler 示例代码%}
```mysql
create table ttt(
	id int auto_increment primary key,
	name varchar(10),
	num int,
	descript varchar(30)
);
```
{%endspoiler%}

分别在name，num以及（name, num）列上创建索引，索引结构如图：

![image-20210805163354585](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210805163401.png)

表中数据如图：

![image-20210805163801217](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210805163801.png)

### 测试一：等值查询

执行语句及输出：

{%spoiler 示例代码%}
```mysql
mysql> explain select num from ttt where num=12\G

*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: ref
possible_keys: idx_t1,idx_tx3
          key: idx_tx3
      key_len: 5
          ref: const
         rows: 1
     filtered: 100.00
        Extra: Using index
1 row in set, 1 warning (0.00 sec)
```
{%endspoiler%}

### 测试二：范围查询

{%spoiler 示例代码%}
```mysql
mysql> explain select num from ttt where num>12\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: range
possible_keys: idx_t1,idx_tx3
          key: idx_tx3
      key_len: 5
          ref: NULL
         rows: 2
     filtered: 100.00
        Extra: Using where; Using index
1 row in set, 1 warning (0.00 sec)

mysql>
mysql>
mysql> explain select num from ttt where num>=12\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: range
possible_keys: idx_t1,idx_tx3
          key: idx_tx3
      key_len: 5
          ref: NULL
         rows: 3
     filtered: 100.00
        Extra: Using where; Using index
1 row in set, 1 warning (0.00 sec)
```
{%endspoiler%}

### 测试三：范围查询（满足ICP使用条件）

{%spoiler 示例代码%}
```mysql
mysql> explain select * from ttt force index(idx_tx3) where num>=12\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: range
possible_keys: idx_tx3
          key: idx_tx3
      key_len: 5
          ref: NULL
         rows: 3
     filtered: 100.00
        Extra: Using index condition
1 row in set, 1 warning (0.00 sec)
```
{%endspoiler%}

### 测试四：范围查询（全表扫描）

{%spoiler 示例代码%}
```mysql
mysql> explain select * from ttt where num>=12\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: ALL
possible_keys: idx_tx3
          key: NULL
      key_len: NULL
          ref: NULL
         rows: 4
     filtered: 75.00
        Extra: Using where
1 row in set, 1 warning (0.00 sec)
```
{%endspoiler%}

## 结论

* Using where表示对数据进行了过滤；
* 满足ICP条件时，显示Using index condition，需要服务层过滤时显示Using where。

## 参考

[[1] MySQL 执行计划中Extra(Using where,Using index,Using index condition,Using index,Using where)的浅析](https://www.cnblogs.com/kerrycode/p/9909093.html)

[[2] 转发: SQL中的where条件，在数据库中提取与应用浅析](https://www.jianshu.com/p/89ec04641e72)

[[3] 官网文档: index-condition-pushdown-optimization](https://dev.mysql.com/doc/refman/8.0/en/index-condition-pushdown-optimization.html)