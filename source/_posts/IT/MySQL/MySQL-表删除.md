---
title: "MySQL-表删除"
isCJKLanguage: true
date: 2021-11-28 20:35:41
updated: 2021-11-28 20:35:41
categories: 
- IT
- MySQL
tags: 
- MySQL
---

# MySQL-删除表

MySQL删除表三种操作：

* delete
* truncate
* drop

## delete

* 逐行删除，可以添加过滤条件（where）
* 删除过程生成undo日志记录
* 删除后，磁盘空间不释放
* 不影响表结构

## truncate

* 清空表内数据，无法应用过滤条件
* 不影响表结构

## drop

* 删除整张表，包括表结构

  

## 删除方式对比

|                | truncate                                    | delete                                                       | drop         |
| -------------- | ------------------------------------------- | ------------------------------------------------------------ | ------------ |
| 执行过程       | DDl,不走事务，不记录undo log，不触发trigger | DML,事务，记录redo和undo log，支持where，触发trigger         | DDL,不走事务 |
| auto_increment | 重置auto_increment                          | 不影响auto_increment(v8.0之前auto_increment保存在内存中，重启MySQL后会影响到auto_increment) | --           |
| 磁盘空间       | 立即删除                                    | 只标记为删除，不做实际删除（被标记的磁盘空间可以被复用）     | 立即删除     |
| 表结构         | 无影响                                      | 无影响                                                       | 删除表结构   |

## 参考

[参考一: MySQL 的 delete、truncate、drop 有什么区别?](https://zhuanlan.zhihu.com/p/270331768)

[参考二: MySQL drop,delete与truncate的区别](https://www.jishuchi.com/read/mysql-interview/2807)