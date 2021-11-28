# Kafka-重平衡

## 重平衡

对消费组内的消费者订阅分区进行重新分配的过程。

## 触发

* 消费组内有新的消费者加入或者旧的消费者退出；
* 消费组内有消费者宕机下线，心跳超时；
* 消费组订阅的主题或者已订阅主题的分区信息发生变化；
* 消费组对应的GroupCoordinator节点发生变化。

## 三阶段

### 一、FIND_COORDINATOR，找到GroupCoordinator

* 如果消费者已经保存了对应的GroupCoordinator节点信息，直接进入下一阶段；

* 否则，向集群的某个节点发送FindCoordinatorRequest请求，查找对应的GroupCoordinator。

  1、请求：发送到集群中负载最小的节点LeastLoadedNode：inFlightRequests中请求数最少的一个节点；

  2、GroupCoordinator的计算方法：

  ​	1） 计算对应的分区号: Utils.abs(groupId.hashcode)%groupMetadataTopicCount，groupMetadataTopicCount为主题__consumer_offsets的分区个数，默认为50;

  ​	2）得到分区号后，该分区leader副本所在的broker节点即为GroupCoordinator节点。

* 组协调者选出分区分配策略
* 组协调者将选出的分区分配策略发送给leader消费者，leader消费者执行分配动作，分配结果发送给每个消费者。 

### 二、JOIN_GROUP，加入消费组

消费者发送JoinGroupRequest请求，请求体中携带该消费者自身能够支持的分区分配策略（取决于消费者客户端的配置）。

GroupCoordinator节点的动作：

* 选出leader消费者：基本可以看作是按照消费者加入消费组的顺序进行选举；

* 选择分区分配策略：

  1）收集每个消费者支持的分区分配策略，组成候选集；

  2）进行投票，每个消费者从候选集中选出第一个自身支持的分配策略，进行投票；*note: 此处不会与消费者交互，由GroupCoordinator根据消费者请求中的分配策略进行统计*

  3）投票最多的策略被选为消费组的分区分配策略，如果有消费者不支持，则抛出异常。

* 发送JoinGroupResponse，leader消费者与普通消费者收到的响应存在不同：leader消费者收到的响应中包含消费组分配策略和订阅topics的信息。



如果是消费者重新加入消费组，需要额外执行下面的动作：

* 如果开启了位移自动提交，那么发送加入请求前需要先提交位移信息；
* 如果添加了自定义的再均衡监听器，在重新加入前实施自定义的规则逻辑；
* 成功加入前禁止心跳检测的运作。

### 三、SYNC_GROUP，同步消费组信息

* leader消费者根据分配策略进行具体的分区分配；
* 消费者向GroupCoordinator发送SyncGroupRequest请求：leader消费者的请求中携带了具体的分配方案；
* GroupCoordinator发送SyncGroupResponse；
* 保存消费组的元数据信息：此时直接保存到GroupCoordinator节点所在的broker即可（因为该节点本身就是对应分区的leader副本所在节点）；

### 四、HEARTBEAT，消费者维持心跳

* 消费者定期上报心跳消息。

## 参考

[参考一: 深入理解Kafka核心设计与实践原理 7.2.2再均衡的原理]()