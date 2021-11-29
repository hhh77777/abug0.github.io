---
title: "MySQL常用操作"
isCJKLanguage: true
date: 2021-11-28 20:35:41
updated: 2021-11-28 20:35:41
categories: 
- IT
- MySQL
tags: 
- MySQL
---

---
title: "MySQL常用操作"
isCJKLanguage: true
date: 2021-08-03 11:09:10
categories: 
- IT
- MySQL
tags: 
- MySQL
---

# MySQL常用操作



* 查看数据库和表

  {%spoiler 示例代码%}
```mysql
  show databases;
  
  show tables;
  ```
{%endspoiler%}

  

* 查看表结构

  {%spoiler 示例代码%}
```mysql
  desc table_name;
  ```
{%endspoiler%}

  

* 查看表上的索引信息

  {%spoiler 示例代码%}
```mysql
  show index from table_name;
  ```
{%endspoiler%}

  

* 查看执行计划

  {%spoiler 示例代码%}
```mysql
  explain sql_stat;
  ```
{%endspoiler%}

  

* 添加列

  {%spoiler 示例代码%}
```mysql
  alter table table_name add column column_name varchar(10);
  ```
{%endspoiler%}

* 添加索引

  {%spoiler 示例代码%}
```mysql
  alter table ttt add index idx_t1(name, num);
  ```
{%endspoiler%}

* 查看和修改事务隔离级别

  {%spoiler 示例代码%}
```mysql
  select @@global.transaction_isolation;
  select @@session.transaction_isolation;
  
  set global|session transaction isolation level REPEATABLE READ|READ COMMITTED|READ UNCOMMITTED|SERIALIZABLE;
  ```
{%endspoiler%}
  
  [官网文档: 13.3.7 SET TRANSACTION 语句](https://dev.mysql.com/doc/refman/8.0/en/set-transaction.html)

* 查看建表语句

  {%spoiler 示例代码%}
```mysql
  show create table table_name;
  ```
{%endspoiler%}

* 查看版本

  {%spoiler 示例代码%}
```mysql
  show variables like "%version%";
  ```
{%endspoiler%}