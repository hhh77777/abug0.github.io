# Kafka

基本概念：

* broker: kafka服务节点

* consumer

* producer

* topic：逻辑概念，使用topic对消息进行归类

* partition

  * 一个topic被划分为多个分区，每个分区实际是一个目录，目录中包含相应分区的消息，以及索引文件
  * 一个分区内会包含多个日志段，每个日志段有一个偏移量索引文件（.index）和一个时间戳索引文件（.timestamp）,以及数据文件（.log）

* segment：一个段可看作一个文件，是消息的物理存储单位

* replications：副本，每个分区都可以有多个副本，以此提高可靠性

* AR/ISR/OSR
  * AR: 所有的副本集合
  * ISR: 与leader副本保持一定程度同步的副本
  * OSR: 滞后于leader副本超出一定程度的副本
  
* LEO/HW
  * LEO: 待写入的下一消息位移（等同于最后一条消息的位移+1）
  * HW: ISR中最小的LEO
  
* leader replication

  * leader副本：当前对外提供的副本
  
* follwer副本：

* 优先副本的选举

  * 优先副本：AR集合中的第一个副本
  * 优先副本的选举：使优先副本成为leader副本
  * 为什么：让leader副本在broker之间尽可能平衡的分布
  * 什么时候选举：定时任务，计算每个broker节点的分区不平衡率（分区不平衡率=非优先副本的leader个数/分区总数），比例超过一定比值（可配置）

* 可靠性：副本

* 高性能：
  * 顺序IO，页缓存
  * 零拷贝-sendfile
  * 网络IO-批处理，数据压缩
  
* 再平衡

* 位移管理-自动提交，手动提交    

* 提高吞吐量：分区，多消费者，参数（acks）

* 某条消息消费失败

* 日志分段

  * 日志段文件大小超过log.segment.bytes
  * 日志段中最大时间戳与当前系统时间差值达到log.roll.ms
  * 索引文件大小达到log.index.size.max.bytes
  * 要写入的消息偏移量与该分段基准偏移量差值达到Integer.MAX_VALUE

* 日志清理

  * 日志删除

    * 基于时间，log.retention.ms
    * 基于大小，log.retention.bytes
    * 基于日志起始偏移量

  * 日志压缩: 对于key相同的消息，只保留最后一个版本

    



* 日志同步机制

  * HW与LEO的更新

* leader epoch

  * 格式：

    <leader_epoch, start_offset>

    leader_epoch: 每次leader发生变更时加1

    start_offset: 当前leader_epoch写入的第一条消息的位移

  * 为什么引入：解决数据丢失和数据不一致问题

  * 数据丢失：leader副本与follower副本间HW同步有延迟，假如在这段时间内follower重启，启动后会清除HW前的消息，如果此时leader也挂掉，那么原follower成为leader，那么folloer_HW--HW间的消息就会丢失；

  * 数据不一致：leader副本与follower副本间HW同步有延迟，假如在这段时间内leader与follower都挂掉，重启后原follower成为新的leader，此时新消息写入，新leader更新自身LEO和HW，如果此时原leader不需要清除信息（因为挂掉前HW已更新），发送FetchRequest，其LEO与HW都刚好与新leader一致，不需要同步消息，此时两者间就出现了不一致的数据；

  * leader epoch如何解决问题：

    * 数据丢失：follower副本恢复时首先向leader发起OffsetsForLeaderEpochRequest，leader收到后返回leader_epoch(请求中包含follower的leader_epoch)对应的LEO。
    * 数据不一致：leader、follower都挂掉，follower成为新的leader，且leader_epoch+1，原leader成为follower，向新leader发起请求，此时新leader中上一纪元的LEO落后于原leader的HW，原leader会截断消息，然后开始同步。

* kafka可靠性：

  * 适当增加副本数
  * 生产者端：acks参数、min.insync.replicas、重试retries参数、retry.backoff.ms
  * 消费者端：重试队列、死信队列、位移提交管理
  * broker：log.flush.interval.ms

* 幂等与事务

* 控制器



## 参考

[[1] Kafka水位(high watermark)与leader epoch的讨论](https://www.cnblogs.com/huxi2b/p/7453543.html)

[[2] 为什么Kafka需要Leader Epoch？](https://t1mek1ller.github.io/2020/02/15/kafka-leader-epoch/)

