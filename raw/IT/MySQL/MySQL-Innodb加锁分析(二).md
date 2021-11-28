# MySQL-Innodb加锁分析(二)

* 环境：windows10，MySQL8.0.21;

* 建表，插入数据：

  ```mysql
  CREATE TABLE ta (a INT NOT NULL, b INT, c INT, INDEX (b)) ENGINE = InnoDB;
  INSERT INTO ta VALUES (1,2,3),(2,2,4);
  ```




## READ UNCOMMITTED与锁

可以读到未提交的数据。写操作会加锁，加锁行为类似RC。

**select...for update和select ... lock in share mode仍会加锁，行锁。**

### 实验

#### select ... for share

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from ta for share;
+---+------+------+
| a | b    | c    |
+---+------+------+
| 1 |    2 |    3 |
| 2 |    2 |    4 |
+---+------+------+
2 rows in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+----------------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME      | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA      |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+----------------+
| INNODB | 1665988586848:1382:1665951760584    |       283140965297504 |        56 |       50 | ttt           | ta          | NULL           | NULL              | NULL            |         1665951760584 | TABLE     | IS            | GRANTED     | NULL           |
| INNODB | 1665988586848:325:4:2:1665951757800 |       283140965297504 |        56 |       50 | ttt           | ta          | NULL           | NULL              | GEN_CLUST_INDEX |         1665951757800 | RECORD    | S,REC_NOT_GAP | GRANTED     | 0x000000000200 |
| INNODB | 1665988586848:325:4:3:1665951757800 |       283140965297504 |        56 |       50 | ttt           | ta          | NULL           | NULL              | GEN_CLUST_INDEX |         1665951757800 | RECORD    | S,REC_NOT_GAP | GRANTED     | 0x000000000201 |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+----------------+
3 rows in set (0.00 sec)
```

#### update

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> update ta set c=5 where b=2;
Query OK, 0 rows affected (0.00 sec)
Rows matched: 2  Changed: 0  Warnings: 0

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME      | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA         |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
| INNODB | 1665988586848:1382:1665951760584    |                118184 |        56 |       83 | ttt           | ta          | NULL           | NULL              | NULL            |         1665951760584 | TABLE     | IX            | GRANTED     | NULL              |
| INNODB | 1665988586848:325:5:2:1665951757800 |                118184 |        56 |       83 | ttt           | ta          | NULL           | NULL              | b               |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 2, 0x000000000200 |
| INNODB | 1665988586848:325:5:3:1665951757800 |                118184 |        56 |       83 | ttt           | ta          | NULL           | NULL              | b               |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 2, 0x000000000201 |
| INNODB | 1665988586848:325:4:2:1665951758144 |                118184 |        56 |       83 | ttt           | ta          | NULL           | NULL              | GEN_CLUST_INDEX |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 0x000000000200    |
| INNODB | 1665988586848:325:4:3:1665951758144 |                118184 |        56 |       83 | ttt           | ta          | NULL           | NULL              | GEN_CLUST_INDEX |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 0x000000000201    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
5 rows in set (0.00 sec)
```



## READ COMMITED与锁

### 概括

* 只对记录加锁，不再加Gap Lock（但是Gap Lock依然会用于外键约束和重复键检查）；
* update和delete语句只对需要更新的行加锁，不满足where条件的行锁会被释放，不需要等到事务完成；
* 半一致性读：update语句，对于已经被锁住的行记录，读取(不加锁)已经提交的最新值判断是否满足where条件，如果满足条件，进行第二次读取，并对其上锁（或者开始等待锁）。**半一致性读只适用于主键索引以及update语句，其他二级索引或者delete语句不适用半一致性读。**

下面是实验验证：

### 实验

#### 锁的提前释放

```mysql
mysql> explain  UPDATE ta SET b = 3 WHERE b = 2 AND c = 3\G
*************************** 1. row ***************************
           id: 1
  select_type: UPDATE
        table: ta
   partitions: NULL
         type: range
possible_keys: b
          key: b
      key_len: 5
          ref: const
         rows: 2
     filtered: 100.00
        Extra: Using where; Using temporary
1 row in set, 1 warning (0.00 sec)


mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> UPDATE ta SET b = 3 WHERE b = 2 AND c = 3;
Query OK, 1 row affected (0.00 sec)
Rows matched: 1  Changed: 1  Warnings: 0

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME      | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA         |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
| INNODB | 1665988586848:1382:1665951760584    |                118209 |        56 |      135 | ttt           | ta          | NULL           | NULL              | NULL            |         1665951760584 | TABLE     | IX            | GRANTED     | NULL              |
| INNODB | 1665988586848:325:5:2:1665951757800 |                118209 |        56 |      135 | ttt           | ta          | NULL           | NULL              | b               |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 2, 0x000000000200 |
| INNODB | 1665988586848:325:4:2:1665951758144 |                118209 |        56 |      135 | ttt           | ta          | NULL           | NULL              | GEN_CLUST_INDEX |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 0x000000000200    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
3 rows in set (0.00 sec)
```

可以看到，根据执行计划，预计加锁范围应该是索引b上的两行记录以及主键上的两行记录，但实际加锁只分别在索引b和主键上锁住了满足条件的一行记录，此处提前释放了不满足where条件的记录锁。



#### 半一致性读-二级索引

| session1（thread_id=56）                               | session2(thread_id=57)                                       |
| ------------------------------------------------------ | ------------------------------------------------------------ |
| begin;<br />UPDATE ta SET b = 3 WHERE b = 2 AND c = 3; |                                                              |
|                                                        | begin;<br />UPDATE ta SET b = 4 WHERE b = 2 AND c = 4;(阻塞) |

看一下锁信息：

```mysql
mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME      | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA         |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
| INNODB | 1665988587680:1382:1665951773768    |                118216 |        57 |       78 | ttt           | ta          | NULL           | NULL              | NULL            |         1665951773768 | TABLE     | IX            | GRANTED     | NULL              |
| INNODB | 1665988587680:325:5:2:1665951770984 |                118216 |        57 |       78 | ttt           | ta          | NULL           | NULL              | b               |         1665951770984 | RECORD    | X,REC_NOT_GAP | WAITING     | 2, 0x000000000200 |
| INNODB | 1665988586848:1382:1665951760584    |                118211 |        56 |      141 | ttt           | ta          | NULL           | NULL              | NULL            |         1665951760584 | TABLE     | IX            | GRANTED     | NULL              |
| INNODB | 1665988586848:325:5:2:1665951757800 |                118211 |        56 |      141 | ttt           | ta          | NULL           | NULL              | b               |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 2, 0x000000000200 |
| INNODB | 1665988586848:325:4:2:1665951758144 |                118211 |        56 |      141 | ttt           | ta          | NULL           | NULL              | GEN_CLUST_INDEX |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 0x000000000200    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+-----------------+-----------------------+-----------+---------------+-------------+-------------------+
5 rows in set (0.00 sec)
```



#### 半一致性读-主键索引

首先更改表结构，将a更改为主键，然后看一下语句的执行计划，结果显示使用的是主键索引，且遍历了整个索引树：

```mysql
mysql> alter table ta add primary key(a);

mysql> explain update ta set b=3 where  c=3\G
*************************** 1. row ***************************
           id: 1
  select_type: UPDATE
        table: ta
   partitions: NULL
         type: index
possible_keys: NULL
          key: PRIMARY
      key_len: 4
          ref: NULL
         rows: 2
     filtered: 100.00
        Extra: Using where
1 row in set, 1 warning (0.00 sec)
```



| session1（thread_id=56）                      | session2(thread_id=57)                               |
| --------------------------------------------- | ---------------------------------------------------- |
| begin;<br />UPDATE ta SET b = 3  WHERE c = 3; |                                                      |
|                                               | begin;<br />UPDATE ta SET b = 4 WHERE c = 4;(未阻塞) |





#### 半一致性读-delete

| session1（thread_id=56）                      | session2(thread_id=57)                        |
| --------------------------------------------- | --------------------------------------------- |
| begin;<br />UPDATE ta SET b = 3  WHERE c = 3; |                                               |
|                                               | begin;<br />DELETE from ta WHERE c = 4;(阻塞) |

查看锁信息：

```mysql
mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988587680:1383:1665951773768    |                118266 |        57 |      102 | ttt           | ta          | NULL           | NULL              | NULL       |         1665951773768 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988587680:326:4:2:1665951771328 |                118266 |        57 |      103 | ttt           | ta          | NULL           | NULL              | PRIMARY    |         1665951771328 | RECORD    | X,REC_NOT_GAP | WAITING     | 1         |
| INNODB | 1665988586848:1383:1665951760584    |                118259 |        56 |      178 | ttt           | ta          | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:326:4:2:1665951757800 |                118259 |        56 |      178 | ttt           | ta          | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 1         |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
4 rows in set (0.00 sec)
```

#### 半一致读-for update/lock in share mode

| session1（thread_id=56）                      | session2(thread_id=57)                                       |
| --------------------------------------------- | ------------------------------------------------------------ |
| begin;<br />UPDATE ta SET b = 3  WHERE c = 3; |                                                              |
|                                               | begin;<br />select * from ta where c=4 lock in share mode(阻塞);<br />select * from ta where c=4 for duapte;(阻塞) |

查看锁信息：

```mysql
mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1383:1665951760584    |                118259 |        56 |      178 | ttt           | ta          | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:326:4:2:1665951757800 |                118259 |        56 |      178 | ttt           | ta          | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 1         |
| INNODB | 1665988587680:1383:1665951773768    |       283140965298336 |        57 |      112 | ttt           | ta          | NULL           | NULL              | NULL       |         1665951773768 | TABLE     | IS            | GRANTED     | NULL      |
| INNODB | 1665988587680:326:4:2:1665951770984 |       283140965298336 |        57 |      112 | ttt           | ta          | NULL           | NULL              | PRIMARY    |         1665951770984 | RECORD    | S,REC_NOT_GAP | WAITING     | 1         |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
4 rows in set (0.00 sec)
```



## desc对加锁的影响

## Gap Lock的合并

## 参考

[[1] 官网文档: innodb-transaction-isolation-levels](https://dev.mysql.com/doc/refman/8.0/en/innodb-transaction-isolation-levels.html)

