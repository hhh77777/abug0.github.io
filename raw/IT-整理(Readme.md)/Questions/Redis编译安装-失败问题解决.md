# Redis编译失败问题解决

redis版本：6.0.5

gcc版本：4.8.5

操作系统：Centos7.6.1810

执行make指令编译redis源码，出错如下：

![image-20201121124723576](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201121124730.png)

解决：

编译指令使用

```
make CC=clang PREFIX=/usr/local/redis install
```

编译成功。

## 问题分析及参考：

[参考一: 问题原因及解决方法](https://www.zhangfangzhou.cn/centos7-devtoolset9-gcc.html)

[参考二: 解决方法](https://www.gitmemory.com/issue/antirez/redis/6286/516992555)