# Redis

* 数据类型
  * 字符串
    *  int
    * embstr
    * raw
  * 列表
    * quicklist+ziplist
  * 有序集合
    * ziplist
    * hashtable+zskiplist
  * 哈希表
    * ziplist
    * hashtable
      * 渐进式rehash
  * 集合
    * intset
      * 升级
    * hashtable



* 数据持久化
  * RDB
  * AOF
* 内存淘汰
  * noevication
  * allkeys-random
  * allkeys-lru
  * allkeys-lfu
  * volatile-random
  * volatile-lru
  * volatile-lfu
  * volatile-ttl

* 