## Linux中的虚拟网络-docker

docker中的网络模型默认使用bridge模式，会在host上创建一个名为docker0的网桥（bridge），关于Docker网络模型的参考见：

[Docker网络模型](https://zhuanlan.zhihu.com/p/98788162)

[Docker网络模型](https://www.jianshu.com/p/a14ebdc37386)

下文使用bridge模式。

bridge模式下实际会为每个容器创建一套单独的网络命名空间，但此时执行ip netns list查看，无输出，原因：ip netns 列出的实际是/var/run/netns目录下的内容，通常只有ip netns add添加的命名空间可通过此方式获取，docker创建的命名空间文件默认是在/var/run/docker/ns目录下。

![docker创建的网络命名空间](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084243.png)

将该目录下内容链接到/var/run/netns下，执行ip netns list，可看到docker创建的命名空间：

![1131即为docker创建的命名空间](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084253.png)

执行docker inspect {container_id}可以查看对应的命名空间（途中标注出的id）：

![docker容器信息](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084257.png)



启动容器时创建会一对veth设备，查看设备信息，可以看到设备类型（veth）以及链接到的命名空间，查看该空间内的设备，可以看到两者恰为一对（分别是if5和4）：

![启动一个docker容器后,查看主机网络](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084301.png)

![veth设备信息](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084307.png)

![查看对端设备](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084313.png)

在host上执行bridge -d fdb查看转发表，分别为容器内发出数据包前后，可以看到第二张图多了一条，02:42:ac:11:00:02正是容器内网卡（该容器只有一张网卡）的mac地址:

![mac转发表](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084330.png)

![mac转发表](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084334.png)