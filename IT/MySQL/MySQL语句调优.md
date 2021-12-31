# MySQL语句调优

## limit深分页优化

* 延迟关联
* 索引
* 书签

[MySQL的LIMIT这么差劲的吗](https://juejin.cn/post/7018170284687491080)

## order by优化

执行方式：

* 全字段排序（单路排序）
* rowid排序（双路排序）



* 索引
* sort_buffer_size优化（8.0.12后sort_buffer动态增长，不再是固定大小）（[8.2.1.16 ORDER BY Optimization](https://dev.mysql.com/doc/refman/8.0/en/order-by-optimization.html)）

* read_rnd_buffer_size(适用于rowid排序场景，关键点在于优化了回表查询，随机IO转为顺序IO)
* max_length_for_sort_data(mysql8.0.20开始废弃)

## MRR（Multi-Range Read Optimization）

[8.2.1.11 Multi-Range Read Optimization](https://dev.mysql.com/doc/refman/8.0/en/mrr-optimization.html)

[关于Mysql 的 ICP、MRR、BKA等特性](http://blog.itpub.net/30135314/viewspace-2708089/)

启用MRR:

```mysql
set optimizer_switch="mrr_cost_based=off";
```



## join算法

NLJ -》 BKA

BNL(mysql8.0.20开始不再支持？？)

Hash Join

BNL和BKA的使用：

> In [`EXPLAIN`](https://dev.mysql.com/doc/refman/8.0/en/explain.html) output, use of BNL for a table is signified when the `Extra` value contains `Using join buffer (Block Nested Loop)` and the `type` value is [`ALL`](https://dev.mysql.com/doc/refman/8.0/en/explain-output.html#jointype_all), [`index`](https://dev.mysql.com/doc/refman/8.0/en/explain-output.html#jointype_index), or [`range`](https://dev.mysql.com/doc/refman/8.0/en/explain-output.html#jointype_range).

[8.2.1.12 Block Nested-Loop and Batched Key Access Joins](https://dev.mysql.com/doc/refman/8.0/en/bnl-bka-optimization.html#bnl-bka-optimizer-hints)





# 参考

[MySQL的server层和存储引擎层是如何交互的](https://juejin.cn/post/6844903856682303495)

[Innodb到底是怎么加锁的](https://juejin.cn/post/7028435335382040589#heading-16)
