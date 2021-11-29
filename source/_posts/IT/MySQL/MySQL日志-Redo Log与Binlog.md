# MySQL日志系统-Redo Log与Binlog

## 一、Bin Log

Bin Log是MySQl服务层的日志。

## 二、Redo Log

### 1、为什么要有redo log？

网上资料都会提到一点：redo log是追加写入。

> MySQL为了减少磁盘的随机IO，因此不会直接更新磁盘数据，而是先更新内存中的数据页，等到合适的时机再对数据页刷盘。而又为了防止MySQL或系统崩溃宕机等问题，又引入了redo log，为crash提供重做恢复机制。

往往还会提到一点：

> redo log是追加写入，性能要高于数据页的随机写。

但是产生了一个疑问是：*对于某个数据页（mysql数据页默认16K）而言，一般而言最多需要四寻址即可定位到磁盘位置（Linux逻辑块大小一般4K，即需要寻址四次），之后都是顺序写入。而反观redo log，写入的时候，必然也要定位到磁盘位置，然后进行写入，并不能看出明显的性能优势，那么，网上说的redo log追加写入性能高到底是为什么呢？*

解答：

*1）设想，一次update/delete/insert可能会影响很多个数据页，而对于每个数据页都需要写回磁盘，而每个数据页的写回，都需要至少一次（通常是16K/4K=4次）的寻道-旋转-传输，这必然大大损耗性能。再看redo log，它记录的是每个数据页的修改，而一页redo log上，可以记录多个数据页的修改，因此需要写回的redo log数据页远少于数据页，这也就大大减少了IO次数（猜想这也是追加写入由于随即写入的原因）。*

*2）数据页可能只被修改了一小部分，但仍然需要写回整页，这增加了不必要的传输字节数。而redo log只记录了数据页的修改，写回的也只是记录下的修改部分，传输量少于数据页。*

### 2、关于redo log

1）redo log记录了数据页的修改；它记录的是“数据页pageN上，偏移量offset处写入n个字节”，引用网络图片：

![redo log通用日志类型](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210319125039.png)

2）redo log是InnoDB特有的日志。

### 3、两阶段提交

#### 更新语句执行流程

a.查找对应的记录，找到对应的数据页，如果数据页在内存中，将更新写入内存中的数据页，否则先从磁盘读入数据页后再进行更新；

b.更新内存中的数据页后暂不写回，而是等待合适的时机再进行刷盘。此时要记录redo log，redo log写入到内存中的缓冲区(log buffer);

c.执行“commit”，发起提交，磁盘写redo log，然后生成bin log写入磁盘。

*note: 此时的磁盘写redo log不一定真的写回了磁盘，可能只是写入到了操作系统的页缓存中。*



#### 事务提交和日志刷盘

两阶段提交：事务提交时执行的动作：

* a. 将内存中的redo log写回磁盘，并标记为‘prepare’；

* b. 生成binlog写入磁盘；

* c. 更新对应的redo log为‘commit’。

  *每条更新语句都会生成redo log记录，但是只有执行commit的时候才会主动进行redo log落盘。但是此处是有可能出现被动刷盘的（内存不足等情况）。*

##### innodb_flush_log_at_trx_commit

* 取值为0：每秒写入到os cache并flush到磁盘，此时commit指令与redo log落盘无关；
* 取值为1：每次commit写入os cache并flush到磁盘；
* 取值为2：每次commit写入os cache，每秒进行一次flush disk动作。

##### sync_binlog

* 取值为0：由OS控制flush到磁盘的时机；
* 取值为N：每写入N条记录flush一次磁盘。

#### 崩溃恢复

* a. 读取redo log并应用，如果redo标识为’commit‘，进行提交；

* b. 如果redo log标识为’prepare‘，需要读取binlog：

  * aa. 如果binlog存在且完整，提交事务；

  * bb. 否则，回滚事务。

    

![redo log与undo log](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20211102101742.webp)

## 参考

[参考一: 极客时间 MySQL45讲: 第一和十五讲](https://time.geekbang.org/column/intro/100020801)

[参考二: 数据库内核月报: MySQL · 引擎特性 · 庖丁解InnoDB之REDO LOG](http://mysql.taobao.org/monthly/2020/02/01/)

[参考三: 数据库内核月报: MySQL · 引擎特性 · InnoDB redo log漫游](http://mysql.taobao.org/monthly/2015/05/01/)

[参考四: 数据库内核月报: MySQL · 引擎特性 · InnoDB 崩溃恢复过程](http://mysql.taobao.org/monthly/2015/06/01/)

[参考五: 一条更新语句在MySQL是怎么执行的](https://gsmtoday.github.io/2019/02/08/how-update-executes-in-mysql/)

[参考六: Innodb引擎 · 基础模块篇(三) · 详解redo log存储结构](https://juejin.cn/post/6895265596985114638)

[浅析MySQL事务中的redo与undo](https://segmentfault.com/a/1190000017888478)
