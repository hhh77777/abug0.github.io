# MVCC与事务隔离

## 一、ACID

**原子性（atomicity）**：事务不可分割。表现为：一个事务中的所有操作，要么全部完成，要么全部不完成。

一致性（consistency）：事务不破坏数据库的完整性，事务前后是从一种一致性状态过渡到另一种一致性状态。比如，银行数据库，事务开始前，所有用户账号储蓄总共为1000，事务结束后，所有用户账号储蓄和依旧为1000。

**隔离性（isolation）**：事务并发执行时，相互间不影响，一种事务所做的修改对另一事务不可见。换言之，事务所看到的修改，一定是该事务开始前已经提交的修改。事务开始后或者未提交的修改统统不可见。

**持久性（durability）**：事务成功执行后，对数据库的修改被持久保存下来。即使发生断电或系统崩溃，依然能恢复到事务成功执行后的状态。

## 二、隔离级别

### （一）数据读取的问题

**丢失修改**：

**脏读**：一个事务读到了另一个事务未提交的修改。

**不可重复读**：事务执行过程中两次读取同一条记录，读到的数据不一致。

**幻读**：事务按同样的查询条件读取数据，读到了之前未读取到的数据。

### （二）隔离级别

**未提交读**：读到了其他事务未提交的数据。

**提交读**：解决了脏读问题，但是存在不可重复读、幻读。

**可重复读**：解决了脏读、不可重复读，但是存在幻读。

**串行化**：解决来脏读、不可重复读、幻读。

**note: MySQL的InnoDB引擎通过MVCC在可重复读的隔离级别上解决了幻读问题。**



## 三、MVCC(Multi version Concurrency Control)

每行记录存在多个版本。

对一行数据修改时，生成一条回滚记录，通过回滚记录可以读取之前版本的值。

### 行记录的结构

每个数据行有三个隐藏列，分别是:

1）DB_ROW_ID：未指定主键时，使用row_id作为主键。（实际上情况比这复杂，唯一非空索引优先级高于row_id）

2）DB_TRX_ID：数据行的版本号，实际就是最后一次修改数据行的事务id。

3）DB_ROLL_PTR：回滚指针，指向前一条undo log。

每一次对记录的修改（update/insert/delete）都会生成一条undo log，同时更新数据行的DB_TRX_ID为当前事务id，DB_ROLL_PTR指向新生成的undo log。

通过DB_ROLL_PTR，对同一行数据的多次修改会形成一条undo log链，在对数据查询时，可以通过DB_ROLL_PTR回溯之前版本的数据。

![image-20210313164919363](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210313164922.png)

### 事务视图：ReadView实现

**note: ReadView与view是两个不同的概念**

先看一下源码（branch-8.0，storage\innobase\include\read0types.h）中定义的变量：

（这里注意到m_low_limit_id的值实际是将给下一个事务分配的id）

![image-20210313091651980](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210313222759.png)

*关于m_up_limit_id和m_low_limit_id的取值问题*

*1）m_low_limit_id：当前系统已分配的最大事务id+1，即将给下一个事务分配的事务id*

*2）m_up_limit_id：m_ids中的最小值，如果m_ids为空，则取当前最大事务id+1，即与m_low_limit_id相同。*



事务启动（***note: 事务的启动时机***）时，生成一个数组，记录当前正在活跃（即已经开始、但还未提交）的事务id。数组中最小的事务id作为低水位，最大值作为高水位。id小于低水位的，说明在事务启动前已经提交了；事务id大于 高水位的，一定是未提交的事务。

![image-20210313091336048](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210313222745.png)

于是对于数据版本中的事务trx_id，有如下三种情况：

1）trx_id<m_up_limit_id，trx_id一定是构造ReadView前已提交的事务，可见；

2）trx_id>=m_low_limit_id,trx_id是构造ReadView时未开始的事务，不可见；

3）m_up_limit_id <= trx_id < m_low_limit_id，进一步判断trx_id是否在m_ids数组中，如果在，则属于未提交事务，不可见，否则属于已提交事务，可见。

### 隔离级别与MVCC

InnoDB通过MVCC机制实现事务的隔离。

在合适的时机（取决于语句和隔离级别）时，生成ReadView视图，通过ReadView实现对数据的一致性读取。每次需要读取某行数据时，就通过ReadView与undo log链来读取出当前事务可见的最新数据。

不同的隔离级别下，ReadView的构造时机不同。

#### RC(Read Committed)

每次执行select时都要生成一次新的ReadView，所以RC下，同一个事务内部两次select之间，可能读到新提交的数据，存在不可重复读和幻读问题。

#### RR(Read Repeated)

第一次执行读语句（即select）时生成ReadView，同一个事务内部的多次select使用同一个ReadView。由于视图一致，所以不会出现不可重复读和幻读问题。

*但是事务开启的方式也会影响ReadView构造时机。*

#### RR: ReadView与事务开启的方式

开启事务的方式也会影响ReadView的构造时机:

1）Begin/Start transaction: 第一次读（select）数据时构造ReadView；

2）Start transaction with consistent snapshot：事务开启的时候就会构造ReadView。

***note: 对数据修改（update/insert/delete）时不会构造ReadView*。**

### ReadView、当前读与快照读

1）当前读：数据更新语句（update/insert/delete）总是先读后写的，而且总是读最新的数据，称为'当前读'。

2）快照读：数据查询（select）在构造的ReadView进行读操作，称为’快照读‘。

对于当前读，总是通过加锁的方式实现并发控制。

***note: select语句加锁时（e.g. in share mode）也是当前读。***

## 四、MVCC与索引

*问题引入：前文讲到，MVCC通过ReadView来构造一致性视图，而实际上，每次要读某行数据时，都是通过事务id和undo log动态计算出当前事务可见的最新数据。那么，索引里的数据总是最新的吗？每个事务读数据时还能否使用索引呢？如果能，又该如何使用？*

对于InnoDB而言，索引可以分为主键索引和非主键索引两类，或者说是聚簇索引和非聚簇索引两类。

先看数据结构：

![image-20210313164655746](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210313164722.png)

![image-20210313164717853](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210313164724.png)

对于非聚簇索引页，max_trx_id表示更新过此页面的最大事务id。

delete bit是删除标志位。（***只从网上查到，未能确认该字段格式等信息***）

### 聚簇索引

使用主键索引查询数据的时候，由于叶子节点保存了完整的数据行信息，可以根据db_trx_id和db_roll_ptr读取出该事务可见的最新数据。

### 非聚簇索引

对于非聚簇索引，情况如下：

1）max_trx_id < m_up_limit_id，可见；否则需要进一步取db_trx_id进行可见性判断；

2）利用索引下推优化。判断该行记录是否满足查询条件，以减少回表（查聚簇索引）次数；

3）满足ICP条件，查询聚簇索引，利用db_trx_id和db_roll_ptr构造视图。

## 五、争论

### （一）MVCC幻读问题

*问题：MVCC存在幻读问题*

**解释**

实际更确切的描述是：MVCC机制下，快照读解决了幻读问题，但是当前读会存在幻读问题。

一段网络原文（见参考七）：

> ## 快照读--只针对Select操作
>
> MVCC的机制。快照读不会产生幻读。因为ReadView生成后就不会发生变化
>
> ## 当前读--针对数据修改操作
>
> 每次执行都会读取最新的记录。（假设要update一条记录，但是在另一个事务中已经delete掉这条数据并且commit了，如果update就会产生冲突，所以在update的时候需要知道最新的数据。）
>
> 结论：**MVCC的机制会使Select语句的快照读避免幻读，但是对于当前读的操作依然会出现幻读。** 
>
> 例子：假如A事务正在查询id<10的所有数据，只存在id为1~7的数据，8、9并不存在，此时B事务向数据库插入id为8的数据，那么事务A就会出现幻读现象，本来是不存在id为8的数据的，但是像出现幻觉一样读取到了，这就是幻读。
>
> 解决办法：加上next-key锁（也就是行锁+gap锁），gap锁会锁着id为8、9的两个位置，阻止事务A读取数据的时候，事务B向数据库插入数据，这样就避免幻读了。
>
> 结论：
>
> - 在快照读情况下，MySQL通过mvcc来避免幻读。
> - 在当前读情况下，MySQL通过next-key来避免幻读



### （二）MySQL 在RR隔离级别下的幻读问题

引用网络图片（图源参考九）：

![MySQL RR幻读问题](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210324191537.png)



#### 分析

​	RR出现幻读的原因是，session1对新插入的行进行了修改操作，导致对应行记录的trx_id被修改为session1的事务id，于是第二次读取时直接读取了最新的记录。

### （三）总结

综合上面两点，当前读下，MySQL RR其实没有完全解决幻读。

## 参考

[参考一: MySQL · 引擎特性 · InnoDB 事务子系统介绍](http://mysql.taobao.org/monthly/2015/12/01/)

[参考二: MVCC和覆盖索引查询](https://www.zhihu.com/question/27674363/answer/38034982)

[参考三: MySQL InnoDB MVCC 机制的原理及实现(提到一个争论点，尽管该争论点实际并不存在争论)](https://chenjiayang.me/2019/06/22/mysql-innodb-mvcc/)

[参考四: 五分钟搞清楚 MVCC 机制(语句执行分析和案例)](https://juejin.cn/post/6844903778026536968)

[参考五: 一文理解Mysql MVCC](https://zhuanlan.zhihu.com/p/66791480)

[参考六: InnoDB Multi-Versioning](https://dev.mysql.com/doc/refman/5.7/en/innodb-multi-versioning.html)

[参考七: 既然MySQL中InnoDB使用MVCC，为什么REPEATABLE-READ不能消除幻读？](https://www.zhihu.com/question/334408495)

[参考八: MySQL 到底是怎么解决幻读的？(提到一个github讨论)](https://chenguoji.com/2019/05/21/mysql-dao-di-shi-zen-me-jie-jue-huan-du-de/)

[参考九: 数据库内核月报: MySQL · 源码分析 · InnoDB Repeatable Read隔离级别之大不同](http://mysql.taobao.org/monthly/2017/06/07/)

[参考十: MySQL RR下的幻读是不是Bug](https://bugs.mysql.com/bug.php?id=63870)