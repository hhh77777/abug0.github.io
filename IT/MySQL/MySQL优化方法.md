# MySQL优化方法

* 可以开启慢查询日志，找出慢查询的sql

  ```mysql
  mysql> show variables like "%slow%";
  +-----------------------------+----------------------------------------+
  | Variable_name               | Value                                  |
  +-----------------------------+----------------------------------------+
  | log_slow_admin_statements   | OFF                                    |
  | log_slow_extra              | OFF                                    |
  | log_slow_replica_statements | OFF                                    |
  | log_slow_slave_statements   | OFF                                    |
  | slow_launch_time            | 2                                      |
  | slow_query_log              | ON                                     |
  | slow_query_log_file         | /var/lib/mysql/VM-24-8-centos-slow.log |
  +-----------------------------+----------------------------------------+
  7 rows in set (0.01 sec)
  
  mysql> show variables like "%long_query%";
  +-----------------+----------+
  | Variable_name   | Value    |
  +-----------------+----------+
  | long_query_time | 0.000000 |
  +-----------------+----------+
  ```

  

* explain查看执行计划

  ```mysql
  mysql> explain select * from employees;
  +----+-------------+-----------+------------+------+---------------+------+---------+------+--------+----------+-------+
  | id | select_type | table     | partitions | type | possible_keys | key  | key_len | ref  | rows   | filtered | Extra |
  +----+-------------+-----------+------------+------+---------------+------+---------+------+--------+----------+-------+
  |  1 | SIMPLE      | employees | NULL       | ALL  | NULL          | NULL | NULL    | NULL | 299335 |   100.00 | NULL  |
  +----+-------------+-----------+------------+------+---------------+------+---------+------+--------+----------+-------+
  1 row in set, 1 warning (0.00 sec)
  ```

* 开启profiling

  ```mysql
  mysql> show variables like "%profil%";
  +------------------------+-------+
  | Variable_name          | Value |
  +------------------------+-------+
  | have_profiling         | YES   |
  | profiling              | ON    |
  | profiling_history_size | 15    |
  +------------------------+-------+
  3 rows in set (0.01 sec)
  ```

  使用效果：

  ```mysql
  mysql> show profiles;
  +----------+------------+------------------------------------+
  | Query_ID | Duration   | Query                              |
  +----------+------------+------------------------------------+
  |        1 | 0.00014150 | select @@version_comment limit 1   |
  |        2 | 0.00071600 | show databases                     |
  |        3 | 0.00018550 | SELECT DATABASE()                  |
  |        4 | 0.00057500 | show databases                     |
  |        5 | 0.00069475 | show tables                        |
  |        6 | 0.00106450 | show tables                        |
  |        7 | 0.00020775 | SELECT DATABASE()                  |
  |        8 | 0.00058600 | show databases                     |
  |        9 | 0.00067600 | show tables                        |
  |       10 | 0.00013800 | explai select * from employees     |
  |       11 | 0.00029950 | explain select * from employees    |
  |       12 | 0.00141325 | show variables like "%slow%"       |
  |       13 | 0.00135125 | show variables like "%long_query%" |
  |       14 | 0.00167225 | show variables like "%profile%"    |
  |       15 | 0.00155400 | show variables like "%profil%"     |
  +----------+------------+------------------------------------+
  15 rows in set, 1 warning (0.00 sec)
  
  mysql> show profile for query 13;
  +----------------------+----------+
  | Status               | Duration |
  +----------------------+----------+
  | starting             | 0.000072 |
  | checking permissions | 0.000016 |
  | Opening tables       | 0.000087 |
  | init                 | 0.000005 |
  | System lock          | 0.000008 |
  | optimizing           | 0.000002 |
  | optimizing           | 0.000007 |
  | statistics           | 0.000020 |
  | preparing            | 0.000017 |
  | statistics           | 0.000004 |
  | preparing            | 0.000011 |
  | executing            | 0.001015 |
  | end                  | 0.000004 |
  | query end            | 0.000008 |
  | closing tables       | 0.000006 |
  | freeing items        | 0.000016 |
  | logging slow query   | 0.000041 |
  | cleaning up          | 0.000013 |
  +----------------------+----------+
  18 rows in set, 1 warning (0.00 sec)
  ```

* 开启optimizer trace

  optimizer trace可以展示sql执行计划的选择和优化过程。

  ```mysql
  mysql> show variables like "%optimizer_trace%";
  +------------------------------+----------------------------------------------------------------------------+
  | Variable_name                | Value                                                                      |
  +------------------------------+----------------------------------------------------------------------------+
  | optimizer_trace              | enabled=off,one_line=off                                                   |
  | optimizer_trace_features     | greedy_search=on,range_optimizer=on,dynamic_range=on,repeated_subselect=on |
  | optimizer_trace_limit        | 1                                                                          |
  | optimizer_trace_max_mem_size | 1048576                                                                    |
  | optimizer_trace_offset       | -1                                                                         |
  +------------------------------+----------------------------------------------------------------------------+
  5 rows in set (0.00 sec)
  ```

  开启：

  ```mysql
  # 开启optimizer trace
  SET optimizer_trace="enabled=on";
  
  # 查询trace信息
  SELECT * FROM INFORMATION_SCHEMA.OPTIMIZER_TRACE;
  ```

  

[遇到慢查询问题可以这样思考与解决](https://www.diaosi.love/archives/%E9%81%87%E5%88%B0%E6%85%A2%E6%9F%A5%E8%AF%A2%E9%97%AE%E9%A2%98%E5%8F%AF%E4%BB%A5%E8%BF%99%E6%A0%B7%E6%80%9D%E8%80%83%E4%B8%8E%E8%A7%A3%E5%86%B3)