# 关于kafka顺序读写的思考.md

[参考一: 关于Kafka broker IO的讨论](https://www.cnblogs.com/huxi2b/p/9860192.html)

[参考二: 聊聊page cache与Kafka之间的事儿](https://cloud.tencent.com/developer/article/1488144)

Kafka高性能的原因之一是对文件的顺序读写，利用了操作系统的预读和后写机制。

两个问题：

1）多个消费者组订阅同一个Topic，对于同一个文件的读写就不是顺序的了，是否会影响预读进而影响Kafka性能？
2）对于同一个Topic，通常会有一个生产者和至少一个消费者，那么对于同一个文件，既读又写，会否导致磁头的来回移动，影响Kafka性能？

## 问题一 多个消费者

