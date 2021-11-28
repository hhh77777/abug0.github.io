# Redis-内存淘汰

Redis内存占用达到maxmemory之后，需要根据配置对内存数据进行淘汰。

## 淘汰策略

* noeviction: 不淘汰数据，对于写命令，返回error。
* allkeys-random: 在所有数据里随机淘汰。
* allkeys-lru: 使用lru算法，在所有数据里进行淘汰。
* allkeys-lfu: 使用lfu算法，在所有数据里进行淘汰。
* volatile-random: 设置了过期时间的数据里随机淘汰。
* volatile-lru: 使用lru算法， 在设置了过期时间的数据里进行淘汰。
* volatile-lfu: 使用lfu算法， 在设置了过期时间的数据里进行淘汰。
* volatile-ttl: 在设置了过期时间的数据里，选择距离过期时最近的数据进行淘汰。

## 相关配置

```
maxmemory <bytes>
maxmemory-policy noeviction

maxmemory-samples 5
replica-ignore-maxmemory yes
```

## 检查时机

![内存淘汰调用链](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20210516122723.png)

如图所示，在每次执行命令的时候会检查当前已使用内存是否超过了maxmomery，如果超过了，则根据配置策略进行处理。

**note: 检查内存使用的时候，会将AOF缓冲区（包括重写缓冲区）和从节点缓冲区的大小排除掉，具体参考evict.c line 396 getMaxmemoryState()。**

**note: 默认情况下从节点不会进行数据淘汰，取决于配置项replica-ignore-maxmemory。**

**note: 主从复制缓冲区导致内存占用过多，进一步触发更多的数据淘汰，可能形成恶性循环。**

​	