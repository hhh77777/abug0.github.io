# MySQL中的索引

哈希索引

B+树索引

聚簇索引

Innodb与MyISAM数据存储结构

主键索引

唯一索引

普通索引（关联change buffer）

联合索引

最左前缀

Indel Condition pushdown(索引下推)

like '%xx'与索引？





## !=和is not null

### 概括

* != 和is not null无法使用索引
* =和is null可以使用索引

```mysql
mysql> select * from ttt;
+----+------+------+----------+
| id | name | num  | descript |
+----+------+------+----------+
|  1 | aa   |    1 | NULL     |
|  5 | dd   |    5 | NULL     |
| 10 | gg   |   10 | NULL     |
| 15 | ll   |   15 | NULL     |
+----+------+------+----------+
4 rows in set (0.02 sec)

mysql> show index from ttt;
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| Table | Non_unique | Key_name | Seq_in_index | Column_name | Collation | Cardinality | Sub_part | Packed | Null | Index_type | Comment | Index_comment | Visible | Expression |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
| ttt   |          0 | PRIMARY  |            1 | id          | A         |           4 |     NULL |   NULL |      | BTREE      |         |               | YES     | NULL       |
| ttt   |          0 | idx_t2   |            1 | name        | A         |           4 |     NULL |   NULL | YES  | BTREE      |         |               | YES     | NULL       |
| ttt   |          0 | idx_t3   |            1 | num         | A         |           4 |     NULL |   NULL | YES  | BTREE      |         |               | YES     | NULL       |
| ttt   |          1 | idx_t1   |            1 | name        | A         |           4 |     NULL |   NULL | YES  | BTREE      |         |               | YES     | NULL       |
| ttt   |          1 | idx_t1   |            2 | num         | A         |           4 |     NULL |   NULL | YES  | BTREE      |         |               | YES     | NULL       |
+-------+------------+----------+--------------+-------------+-----------+-------------+----------+--------+------+------------+---------+---------------+---------+------------+
5 rows in set (0.02 sec)
```



```mysql
mysql> explain select num from ttt where num=5\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: const
possible_keys: idx_t3
          key: idx_t3
      key_len: 5
          ref: const
         rows: 1
     filtered: 100.00
        Extra: Using index
1 row in set, 1 warning (0.00 sec)


mysql> explain select num from ttt where num!=5\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: range
possible_keys: idx_t3
          key: idx_t3
      key_len: 5
          ref: NULL
         rows: 3
     filtered: 100.00
        Extra: Using where; Using index
1 row in set, 1 warning (0.00 sec)


mysql> explain select num from ttt where num is null\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: ref
possible_keys: idx_t3,idx_t1
          key: idx_t3
      key_len: 5
          ref: const
         rows: 1
     filtered: 100.00
        Extra: Using where; Using index
1 row in set, 1 warning (0.00 sec)


mysql> explain select num from ttt where num is not null\G
*************************** 1. row ***************************
           id: 1
  select_type: SIMPLE
        table: ttt
   partitions: NULL
         type: index
possible_keys: idx_t3,idx_t1
          key: idx_t3
      key_len: 5
          ref: NULL
         rows: 4
     filtered: 100.00
        Extra: Using where; Using index
1 row in set, 1 warning (0.00 sec)
```

