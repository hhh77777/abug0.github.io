---

---

# MySQL-Innodb加锁分析

Innodb锁机制是通过在索引加锁实现的。

## 环境和数据准备

* 环境：windows10，MySQL8.0.21;

* 隔离级别：RR；

* 建表，插入数据：

  ```mysql
   CREATE TABLE `ttt` (
    `id` int NOT NULL AUTO_INCREMENT,
    `name` varchar(10) DEFAULT NULL,
    `num` int DEFAULT NULL,
    `descript` varchar(30) DEFAULT NULL,
    PRIMARY KEY (`id`),
    UNIQUE KEY `idx_t2` (`name`),
    UNIQUE KEY `idx_t3` (`num`),
    KEY `idx_t1` (`name`,`num`)
  );
  
  insert into ttt(id, name, num) values(1, 'aa', 1), (5, 'dd', 5), (10, 'gg', 10), (15, 'll', 15);
  ```

  

## 加锁规则

极客时间林晓斌《MySQL实战45讲》中对MySQL加锁规则的总结及补充：

* 查找过程中访问到的数据才会加锁；

* 加锁的基本单位是Next-Key Lock;

* 唯一索引上的等值查询，命中记录时退化为行锁：主键索引会退化为行锁，二级唯一索引没有退化为行锁；

* 索引上的等值查询，向右遍历且最后一个值不满足等值条件时，退化为Gap Lock：主键索引上向右遍历且最后一个值不满足条件时，即使是范围查询也会退化为Gap Lock;

* 唯一索引上的范围查询，会查询到不满足条件的第一个值为止：二级唯一索引存在此问题，但是主键索引优化了此问题：访问到当前的最大值时，会对下一个记录（supremum）加锁，其他情况下则不会。

  

另外补充一条：

* RR级别下，不满足where条件的记录不会提前释放锁：如果使用了二级索引，那么主键索引上只会对需要回表访问的记录加锁（考虑ICP）。



## 总结与概括

* 首先定位到扫描区间内的第一个记录，开始往下遍历，扫描到的数据加锁；
* 如果是order by ... desc，则要对这条记录的后面一条记录加LOCK_GAP(需满足加GAP Lock的条件，比如隔离级别大于等于可重复读等);
* 如果是精确匹配（where条件为=），且该记录不满足条件，则对记录加一条LOCK_GAP，然后结束加锁过程；
* 到这一步需要对该记录进行判断：
  * 唯一性搜索且记录没被删除，加LOCK_REC_NOT_GAP
  * 聚簇索引上 的>=条件，且该记录刚好是开始条件，加LOCK_REC_NOT_GAP；
  * 聚簇索引上的查询，而且是第一次定位记录或者是向后搜索（区别于order by desc的情况）且该记录不满足条件，加LOCK_GAP；
  * 其他情况加Next-Key Lock。



### 说明

#### 访问到的数据才会加锁

Innodb加锁都是在索引上加的。

#### 加锁单位Next-Key Lock

#### 唯一索引等值查询的退化

#### 等值查询与范围查询

举例：

```mysql
select * from ttt where num>=5 and num<=10;
```

该语句的执行方式：首先用num=5在索引中进行定位，所以这是一个等值查询，而后向右遍历检查num是否满足num<=10的条件，这一步是范围查询。



## 读锁-主键索引

### 等值查询（命中记录）：行锁

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql>
mysql>
mysql>
mysql> select * from ttt where id=5 lock in share mode;
+----+------+------+----------+
| id | name | num  | descript |
+----+------+------+----------+
|  5 | dd   |    5 | NULL     |
+----+------+------+----------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks\G
*************************** 1. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:1381:1665951760584
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 43
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: NULL
OBJECT_INSTANCE_BEGIN: 1665951760584
            LOCK_TYPE: TABLE
            LOCK_MODE: IS
          LOCK_STATUS: GRANTED
            LOCK_DATA: NULL
*************************** 2. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:324:4:3:1665951757800
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 43
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: PRIMARY
OBJECT_INSTANCE_BEGIN: 1665951757800
            LOCK_TYPE: RECORD
            LOCK_MODE: S,REC_NOT_GAP
          LOCK_STATUS: GRANTED
            LOCK_DATA: 5
2 rows in set (0.00 sec)
```

![image-20210808191902997](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210808191903.png)

可以看到上了两把锁，一把在表上的意向共享锁，另一把是主键上的行锁，锁住的的是id=2这一行。

### 等值查询（未命中记录）：间隙锁

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from ttt where id=2 lock in share mode;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks\G
*************************** 1. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:1381:1665951760584
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 39
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: NULL
OBJECT_INSTANCE_BEGIN: 1665951760584
            LOCK_TYPE: TABLE
            LOCK_MODE: IS
          LOCK_STATUS: GRANTED
            LOCK_DATA: NULL
*************************** 2. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:324:4:3:1665951757800
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 39
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: PRIMARY
OBJECT_INSTANCE_BEGIN: 1665951757800
            LOCK_TYPE: RECORD
            LOCK_MODE: S,GAP
          LOCK_STATUS: GRANTED
            LOCK_DATA: 5
2 rows in set (0.00 sec)
```

依旧是两把锁，不过第二把锁由行锁变成了Gap Lock，锁住得得是（1， 5）这个间隙。

### 范围查询

#### 命中记录

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from ttt where id>=5 and id<=10 lock in share mode;
+----+------+------+----------+
| id | name | num  | descript |
+----+------+------+----------+
|  5 | dd   |    5 | NULL     |
| 10 | gg   |   10 | NULL     |
+----+------+------+----------+
2 rows in set (0.00 sec)

mysql> select * from performance_schema.data_locks\G
*************************** 1. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:1381:1665951760584
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 88
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: NULL
OBJECT_INSTANCE_BEGIN: 1665951760584
            LOCK_TYPE: TABLE
            LOCK_MODE: IS
          LOCK_STATUS: GRANTED
            LOCK_DATA: NULL
*************************** 2. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:324:4:3:1665951757800
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 88
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: PRIMARY
OBJECT_INSTANCE_BEGIN: 1665951757800
            LOCK_TYPE: RECORD
            LOCK_MODE: S,REC_NOT_GAP
          LOCK_STATUS: GRANTED
            LOCK_DATA: 5
*************************** 3. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:324:4:4:1665951758144
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 88
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: PRIMARY
OBJECT_INSTANCE_BEGIN: 1665951758144
            LOCK_TYPE: RECORD
            LOCK_MODE: S
          LOCK_STATUS: GRANTED
            LOCK_DATA: 10
3 rows in set (0.00 sec)
```

#### 未命中记录

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from ttt where id>5 and id<10 lock in share mode;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks\G
*************************** 1. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:1381:1665951760584
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 96
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: NULL
OBJECT_INSTANCE_BEGIN: 1665951760584
            LOCK_TYPE: TABLE
            LOCK_MODE: IS
          LOCK_STATUS: GRANTED
            LOCK_DATA: NULL
*************************** 2. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:324:4:4:1665951757800
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 96
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: PRIMARY
OBJECT_INSTANCE_BEGIN: 1665951757800
            LOCK_TYPE: RECORD
            LOCK_MODE: S,GAP
          LOCK_STATUS: GRANTED
            LOCK_DATA: 10
2 rows in set (0.00 sec)
```

#### 总结

对比命中记录和未命中记录的加锁情况，可以看到：

* where条件里的等值查询加锁情况与前一节相同；
* 向右遍历且最后一个值不满足条件时只加了Gap Lock，而非Next-Key Lock。**此处与优化2有出入**
* 范围查询，向右遍历时，第一个不满足条件的记录并未上锁，此处与规则所述有出入（此处实际有更复杂的情况，参考下一节[范围查询（唯一索引bug）]）；

### 范围查询（唯一索引bug）

#### 四种情况

* where右值（<）为表中记录最大值：

  * <

  ```mysql
  mysql> begin;
  Query OK, 0 rows affected (0.00 sec)
  
  mysql> select * from ttt where id>10 and id<15 lock in share mode;
  Empty set (0.00 sec)
  
  mysql> select * from performance_schema.data_locks;
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      207 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
  | INNODB | 1665988586848:324:4:5:1665951757800 |       283140965297504 |        53 |      207 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | S,GAP     | GRANTED     | 15        |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  2 rows in set (0.00 sec)
  ```

  

  * <=

  ```mysql
  mysql> begin;
  Query OK, 0 rows affected (0.00 sec)
  
  mysql> select * from ttt where id>5 and id<=15 lock in share mode;
  +----+------+------+----------+
  | id | name | num  | descript |
  +----+------+------+----------+
  | 10 | gg   |   10 | NULL     |
  | 15 | ll   |   15 | NULL     |
  +----+------+------+----------+
  2 rows in set (0.00 sec)
  
  mysql> select * from performance_schema.data_locks;
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+------------------------+
  | ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA              |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+------------------------+
  | INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      221 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL                   |
  | INNODB | 1665988586848:324:4:1:1665951757800 |       283140965297504 |        53 |      221 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | S         | GRANTED     | supremum pseudo-record |
  | INNODB | 1665988586848:324:4:4:1665951757800 |       283140965297504 |        53 |      221 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | S         | GRANTED     | 10                     |
  | INNODB | 1665988586848:324:4:5:1665951757800 |       283140965297504 |        53 |      221 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | S         | GRANTED     | 15                     |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+------------------------+
  4 rows in set (0.00 sec)
  ```

  

* where右值（<）不是最大值：

  * <

  ```mysql
  mysql> begin;
  Query OK, 0 rows affected (0.00 sec)
  
  mysql> select * from ttt where id>5 and id<10 lock in share mode;
  Empty set (0.00 sec)
  
  mysql> select * from performance_schema.data_locks;
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      212 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
  | INNODB | 1665988586848:324:4:4:1665951757800 |       283140965297504 |        53 |      212 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | S,GAP     | GRANTED     | 10        |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  ```

  

  * <=

  ```mysql
  mysql> begin;
  Query OK, 0 rows affected (0.00 sec)
  
  mysql> select * from ttt where id>5 and id<=10 lock in share mode;
  +----+------+------+----------+
  | id | name | num  | descript |
  +----+------+------+----------+
  | 10 | gg   |   10 | NULL     |
  +----+------+------+----------+
  1 row in set (0.00 sec)
  
  mysql> select * from performance_schema.data_locks;
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      216 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
  | INNODB | 1665988586848:324:4:4:1665951757800 |       283140965297504 |        53 |      216 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | S         | GRANTED     | 10        |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  2 rows in set (0.00 sec)
  ```

#### 总结

* 可以看到对于where右值操作符为<的情况，加锁规则一致，但是对于<=，如果操作数为最大值，那么会对supremum 加上Next-Key Lock。
* 对于本文开头的加锁规则，”唯一索引上的范围查询，会查询到不满足条件的第一个值为止“，这一点在本版本基本已优化（忽略supremum）。
* 只有对于supremum的加锁，暂未找到原因。

## 读锁-非主键唯一索引

### 等值查询(命中记录): 行锁

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num=5 lock in share mode;
+------+
| num  |
+------+
|    5 |
+------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks\G
*************************** 1. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:1381:1665951760584
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 248
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: NULL
OBJECT_INSTANCE_BEGIN: 1665951760584
            LOCK_TYPE: TABLE
            LOCK_MODE: IS
          LOCK_STATUS: GRANTED
            LOCK_DATA: NULL
*************************** 2. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:324:6:3:1665951757800
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 248
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: idx_t3
OBJECT_INSTANCE_BEGIN: 1665951757800
            LOCK_TYPE: RECORD
            LOCK_MODE: S,REC_NOT_GAP
          LOCK_STATUS: GRANTED
            LOCK_DATA: 5, 5
2 rows in set (0.00 sec)
```

### 等值查询(未命中记录)：间隙锁

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num=6 lock in share mode;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks\G
*************************** 1. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:1381:1665951760584
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 252
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: NULL
OBJECT_INSTANCE_BEGIN: 1665951760584
            LOCK_TYPE: TABLE
            LOCK_MODE: IS
          LOCK_STATUS: GRANTED
            LOCK_DATA: NULL
*************************** 2. row ***************************
               ENGINE: INNODB
       ENGINE_LOCK_ID: 1665988586848:324:6:4:1665951757800
ENGINE_TRANSACTION_ID: 283140965297504
            THREAD_ID: 53
             EVENT_ID: 252
        OBJECT_SCHEMA: ttt
          OBJECT_NAME: ttt
       PARTITION_NAME: NULL
    SUBPARTITION_NAME: NULL
           INDEX_NAME: idx_t3
OBJECT_INSTANCE_BEGIN: 1665951757800
            LOCK_TYPE: RECORD
            LOCK_MODE: S,GAP
          LOCK_STATUS: GRANTED
            LOCK_DATA: 10, 10
2 rows in set (0.00 sec)
```



### 范围查询

#### 命中记录

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>=5 and num<=10 lock in share mode;
+------+
| num  |
+------+
|    5 |
|   10 |
+------+
2 rows in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      272 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:3:1665951757800 |       283140965297504 |        53 |      272 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 5, 5      |
| INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      272 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 10, 10    |
| INNODB | 1665988586848:324:6:5:1665951757800 |       283140965297504 |        53 |      272 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 15, 15    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
4 rows in set (0.00 sec)
```



#### 未命中记录

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>5 and num<10 lock in share mode;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      268 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      268 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 10, 10    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
2 rows in set (0.00 sec)
```



#### 总结

* where里的左值(<=)应该是一个等值查询，但命中时并未退化为行锁，此处与主键索引以及加锁规则所述有出入；

* 向右遍历且右值不满足条件时未退化为Gap Lock，此处与规则相匹配（因为右值实际时范围查询，而非等值查询），这是与主键索引有区别的一点；
* 向右遍历，依然需要访问到不满足条件的第一个值，此处与规则匹配，但与主键访问时的情况不同。

### 范围查询（唯一索引bug）

#### 四种情况

* where右值为最大值：

  * <

  ```mysql
  mysql> begin;
  Query OK, 0 rows affected (0.00 sec)
  
  mysql> select num from ttt where num>5 and num<15 lock in share mode;
  +------+
  | num  |
  +------+
  |   10 |
  +------+
  1 row in set (0.00 sec)
  
  mysql> select * from performance_schema.data_locks;
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      277 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
  | INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      277 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 10, 10    |
  | INNODB | 1665988586848:324:6:5:1665951757800 |       283140965297504 |        53 |      277 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 15, 15    |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  3 rows in set (0.00 sec)
  ```

  

  * <=

  ```mysql
  mysql> begin;
  Query OK, 0 rows affected (0.00 sec)
  
  mysql> select num from ttt where num>5 and num<=15 lock in share mode;
  +------+
  | num  |
  +------+
  |   10 |
  |   15 |
  +------+
  2 rows in set (0.00 sec)
  
  mysql> select * from performance_schema.data_locks;
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+------------------------+
  | ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA              |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+------------------------+
  | INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      281 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL                   |
  | INNODB | 1665988586848:324:6:1:1665951757800 |       283140965297504 |        53 |      281 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | supremum pseudo-record |
  | INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      281 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 10, 10                 |
  | INNODB | 1665988586848:324:6:5:1665951757800 |       283140965297504 |        53 |      281 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 15, 15                 |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+------------------------+
  4 rows in set (0.00 sec)
  ```

  

* where右值不是最大值：

  * <

  ```mysql
  mysql> begin;
  Query OK, 0 rows affected (0.00 sec)
  
  mysql> select num from ttt where num>5 and num<10 lock in share mode;
  Empty set (0.00 sec)
  
  mysql> select * from performance_schema.data_locks;
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      287 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
  | INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      287 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 10, 10    |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  2 rows in set (0.00 sec)
  ```

  

  * <=

  ```mysql
  mysql> begin;
  Query OK, 0 rows affected (0.00 sec)
  
  mysql> select num from ttt where num>5 and num<=10 lock in share mode;
  +------+
  | num  |
  +------+
  |   10 |
  +------+
  1 row in set (0.00 sec)
  
  mysql> select * from performance_schema.data_locks;
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  | INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      293 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
  | INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      293 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 10, 10    |
  | INNODB | 1665988586848:324:6:5:1665951757800 |       283140965297504 |        53 |      293 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 15, 15    |
  +--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
  3 rows in set (0.00 sec)
  ```

  

#### 总结

* 基本与主键索引表现一致；
* 非最大值时主键索引不会对不满足条件的第一个记录加锁，但是非主键唯一索引会加锁，这是区别。

## 读锁-非主键非唯一索引

修改表索引，将num上的索引改为非唯一索引：

```mysql
alter table ttt drop index idx_t3;

alter table ttt add index idx_t3(num);
```



### 等值查询(命中记录)：Next-Key Lock+Gap Lock

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num=5 lock in share mode;
+------+
| num  |
+------+
|    5 |
+------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      308 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:3:1665951757800 |       283140965297504 |        53 |      308 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 5, 5      |
| INNODB | 1665988586848:324:6:4:1665951758144 |       283140965297504 |        53 |      308 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951758144 | RECORD    | S,GAP     | GRANTED     | 10, 10    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
3 rows in set (0.00 sec)
```

### 等值查询（未命中记录）： 间隙锁

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num=6 lock in share mode;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      312 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      312 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S,GAP     | GRANTED     | 10, 10    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
2 rows in set (0.00 sec)
```



### 范围查询

#### 命中记录

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>=5 and num<=10 lock in share mode;
+------+
| num  |
+------+
|    5 |
|   10 |
+------+
2 rows in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      320 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:3:1665951757800 |       283140965297504 |        53 |      320 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 5, 5      |
| INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      320 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 10, 10    |
| INNODB | 1665988586848:324:6:5:1665951757800 |       283140965297504 |        53 |      320 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 15, 15    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
4 rows in set (0.00 sec)
```



#### 未命中记录

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>5 and num<10 lock in share mode;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |       283140965297504 |        53 |      316 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IS        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:4:1665951757800 |       283140965297504 |        53 |      316 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | S         | GRANTED     | 10, 10    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
2 rows in set (0.00 sec)
```



## 写锁-主键索引

### 等值查询(命中记录)

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from ttt where id=5 for update;
+----+------+------+----------+
| id | name | num  | descript |
+----+------+------+----------+
|  5 | dd   |    5 | NULL     |
+----+------+------+----------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118109 |        53 |      336 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:4:3:1665951757800 |                118109 |        53 |      336 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 5         |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
2 rows in set (0.00 sec)
```

### 等值查询（未命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from ttt where id=6 for update;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118110 |        53 |      340 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:4:4:1665951757800 |                118110 |        53 |      340 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | X,GAP     | GRANTED     | 10        |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
2 rows in set (0.00 sec)
```



### 范围查询(命中记录)

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from ttt where id>5 and id<10 for update;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118111 |        53 |      344 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:4:4:1665951757800 |                118111 |        53 |      344 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | X,GAP     | GRANTED     | 10        |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
2 rows in set (0.00 sec)
```



### 范围查询（未命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select * from ttt where id>=5 and id<=10 for update;
+----+------+------+----------+
| id | name | num  | descript |
+----+------+------+----------+
|  5 | dd   |    5 | NULL     |
| 10 | gg   |   10 | NULL     |
+----+------+------+----------+
2 rows in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118112 |        53 |      348 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:4:3:1665951757800 |                118112 |        53 |      348 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 5         |
| INNODB | 1665988586848:324:4:4:1665951758144 |                118112 |        53 |      348 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X             | GRANTED     | 10        |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
3 rows in set (0.00 sec)
```



## 写锁-非主键唯一索引

### 等值查询（命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num=5 for update;
+------+
| num  |
+------+
|    5 |
+------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118134 |        53 |      386 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:3:1665951757800 |                118134 |        53 |      386 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X,REC_NOT_GAP | GRANTED     | 5, 5      |
| INNODB | 1665988586848:324:4:3:1665951758144 |                118134 |        53 |      386 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 5         |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
3 rows in set (0.00 sec)
```



### 等值查询（未命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num=6 for update;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118135 |        53 |      390 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:4:1665951757800 |                118135 |        53 |      390 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X,GAP     | GRANTED     | 10, 10    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
2 rows in set (0.00 sec)
```



### 范围查询（命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>=5 and num<=10 for update;
+------+
| num  |
+------+
|    5 |
|   10 |
+------+
2 rows in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118137 |        53 |      398 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:3:1665951757800 |                118137 |        53 |      398 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 5, 5      |
| INNODB | 1665988586848:324:6:4:1665951757800 |                118137 |        53 |      398 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 10, 10    |
| INNODB | 1665988586848:324:6:5:1665951757800 |                118137 |        53 |      398 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 15, 15    |
| INNODB | 1665988586848:324:4:3:1665951758144 |                118137 |        53 |      398 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 5         |
| INNODB | 1665988586848:324:4:4:1665951758144 |                118137 |        53 |      398 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 10        |
| INNODB | 1665988586848:324:4:5:1665951758144 |                118137 |        53 |      398 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 15        |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
7 rows in set (0.00 sec)
```



### 范围查询（未命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>5 and num<15 for update;
+------+
| num  |
+------+
|   10 |
+------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118136 |        53 |      394 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:4:1665951757800 |                118136 |        53 |      394 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 10, 10    |
| INNODB | 1665988586848:324:6:5:1665951757800 |                118136 |        53 |      394 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 15, 15    |
| INNODB | 1665988586848:324:4:4:1665951758144 |                118136 |        53 |      394 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 10        |
| INNODB | 1665988586848:324:4:5:1665951758144 |                118136 |        53 |      394 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 15        |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
5 rows in set (0.00 sec)
```



## 写锁-非主键非唯一索引

### 等值查询（命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num=5 for update;
+----+------+------+----------+
| id | name | num  | descript |
+----+------+------+----------+
|  5 | dd   |    5 | NULL     |
+----+------+------+----------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118113 |        53 |      352 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:3:1665951757800 |                118113 |        53 |      352 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 5, 5      |
| INNODB | 1665988586848:324:4:3:1665951758144 |                118113 |        53 |      352 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 5         |
| INNODB | 1665988586848:324:6:4:1665951758488 |                118113 |        53 |      352 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951758488 | RECORD    | X,GAP         | GRANTED     | 10, 10    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
4 rows in set (0.00 sec)
```

### 等值查询（未命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num=6 for update;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118115 |        53 |      360 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX        | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:4:1665951757800 |                118115 |        53 |      360 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X,GAP     | GRANTED     | 10, 10    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+-----------+-------------+-----------+
2 rows in set (0.00 sec)
```

### 范围查询（命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>=5 and num<=10 for update;
+------+
| num  |
+------+
|    5 |
|   10 |
+------+
2 rows in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118116 |        53 |      367 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:3:1665951757800 |                118116 |        53 |      367 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 5, 5      |
| INNODB | 1665988586848:324:6:4:1665951757800 |                118116 |        53 |      367 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 10, 10    |
| INNODB | 1665988586848:324:6:5:1665951757800 |                118116 |        53 |      367 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 15, 15    |
| INNODB | 1665988586848:324:4:3:1665951758144 |                118116 |        53 |      367 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 5         |
| INNODB | 1665988586848:324:4:4:1665951758144 |                118116 |        53 |      367 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 10        |
| INNODB | 1665988586848:324:4:5:1665951758144 |                118116 |        53 |      367 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 15        |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
7 rows in set (0.00 sec)
```



### 范围查询（未命中记录）

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>5 and num<15 for update;
+------+
| num  |
+------+
|   10 |
+------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118118 |        53 |      375 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:4:1665951757800 |                118118 |        53 |      375 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 10, 10    |
| INNODB | 1665988586848:324:6:5:1665951757800 |                118118 |        53 |      375 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 15, 15    |
| INNODB | 1665988586848:324:4:4:1665951758144 |                118118 |        53 |      375 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 10        |
| INNODB | 1665988586848:324:4:5:1665951758144 |                118118 |        53 |      375 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 15        |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
5 rows in set (0.00 sec)
```

***note: 此处主键上id=15这一行也被锁住了***

## 写锁-ICP

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql>
mysql> select * from ttt force index(idx_t1) where name>'aa' and name<'ll' and num=10 for update;
+----+------+------+----------+
| id | name | num  | descript |
+----+------+------+----------+
| 10 | gg   |   10 | NULL     |
+----+------+------+----------+
1 row in set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+--------------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA    |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+--------------+
| INNODB | 1665988586848:1381:1665951760584    |                118146 |        53 |      444 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL         |
| INNODB | 1665988586848:324:7:3:1665951757800 |                118146 |        53 |      444 | ttt           | ttt         | NULL           | NULL              | idx_t1     |         1665951757800 | RECORD    | X             | GRANTED     | 'dd', 5, 5   |
| INNODB | 1665988586848:324:7:4:1665951757800 |                118146 |        53 |      444 | ttt           | ttt         | NULL           | NULL              | idx_t1     |         1665951757800 | RECORD    | X             | GRANTED     | 'gg', 10, 10 |
| INNODB | 1665988586848:324:7:5:1665951757800 |                118146 |        53 |      444 | ttt           | ttt         | NULL           | NULL              | idx_t1     |         1665951757800 | RECORD    | X             | GRANTED     | 'll', 15, 15 |
| INNODB | 1665988586848:324:4:4:1665951758144 |                118146 |        53 |      444 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 10           |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+--------------+
5 rows in set (0.00 sec)
```

**索引下推时注意主键索引上的锁，通过索引已经过滤掉的记录并未在主键上加锁。**

## 补充

补充一个测试：

```mysql
mysql> begin;
Query OK, 0 rows affected (0.00 sec)

mysql> select num from ttt where num>5 and num<15 and id!=10 for update;
Empty set (0.00 sec)

mysql> select * from performance_schema.data_locks;
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| ENGINE | ENGINE_LOCK_ID                      | ENGINE_TRANSACTION_ID | THREAD_ID | EVENT_ID | OBJECT_SCHEMA | OBJECT_NAME | PARTITION_NAME | SUBPARTITION_NAME | INDEX_NAME | OBJECT_INSTANCE_BEGIN | LOCK_TYPE | LOCK_MODE     | LOCK_STATUS | LOCK_DATA |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
| INNODB | 1665988586848:1381:1665951760584    |                118140 |        53 |      416 | ttt           | ttt         | NULL           | NULL              | NULL       |         1665951760584 | TABLE     | IX            | GRANTED     | NULL      |
| INNODB | 1665988586848:324:6:4:1665951757800 |                118140 |        53 |      416 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 10, 10    |
| INNODB | 1665988586848:324:6:5:1665951757800 |                118140 |        53 |      416 | ttt           | ttt         | NULL           | NULL              | idx_t3     |         1665951757800 | RECORD    | X             | GRANTED     | 15, 15    |
| INNODB | 1665988586848:324:4:4:1665951758144 |                118140 |        53 |      416 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 10        |
| INNODB | 1665988586848:324:4:5:1665951758144 |                118140 |        53 |      416 | ttt           | ttt         | NULL           | NULL              | PRIMARY    |         1665951758144 | RECORD    | X,REC_NOT_GAP | GRANTED     | 15        |
+--------+-------------------------------------+-----------------------+-----------+----------+---------------+-------------+----------------+-------------------+------------+-----------------------+-----------+---------------+-------------+-----------+
5 rows in set (0.00 sec)
```

关于这句的执行计划：

```mysql
mysql> explain  select num from ttt where num>5 and num<15 and id!=10 for update;
+----+-------------+-------+------------+-------+-----------------------+--------+---------+------+------+----------+--------------------------+
| id | select_type | table | partitions | type  | possible_keys         | key    | key_len | ref  | rows | filtered | Extra                    |
+----+-------------+-------+------------+-------+-----------------------+--------+---------+------+------+----------+--------------------------+
|  1 | SIMPLE      | ttt   | NULL       | range | PRIMARY,idx_t3,idx_t1 | idx_t3 | 5       | NULL |    1 |    75.00 | Using where; Using index |
+----+-------------+-------+------------+-------+-----------------------+--------+---------+------+------+----------+--------------------------+
1 row in set, 1 warning (0.00 sec)
```

**这个地方id=10这一行并不符合条件，但是主键上依然锁住了id=10。**

## 参考

[[1] 超全面 MySQL 语句加锁分析](https://learnku.com/articles/40624)

[[2] MySQL 中关于gap lock / next-key lock 的一个问题](https://helloworlde.github.io/blog/blog/MySQL/MySQL-%E4%B8%AD%E5%85%B3%E4%BA%8Egap-lock-next-key-lock-%E7%9A%84%E4%B8%80%E4%B8%AA%E9%97%AE%E9%A2%98.html)

[[3] Mysql锁：灵魂七拷问](https://tech.youzan.com/seven-questions-about-the-lock-of-mysql/)

[[4] MySQL 加锁处理分析（MVVC、快照读、当前读、GAP锁（间隙锁））](https://www.huaweicloud.com/articles/f571bafcbe55475cd94d1f2f65e729a9.html)

[[5] MySQL官网: 15.7.3 Locks Set by Different SQL Statements in InnoDB](https://dev.mysql.com/doc/refman/8.0/en/innodb-locks-set.html)

[[6] Innodb到底是怎么加锁的](https://juejin.cn/post/7028435335382040589#heading-9)

