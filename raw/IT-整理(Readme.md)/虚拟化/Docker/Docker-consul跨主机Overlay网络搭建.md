# Docker跨主机网络搭建--consul

[参考一: consul初探-从安装到运行](https://www.cnblogs.com/viter/p/11018953.html)

[参考二: consul安装和基本使用](https://sanyuesha.com/2017/11/15/what-about-consul/)

## 一、需要搭建consul

注意事项：搭建consul集群前需确保每台服务器的hostname不同，且关闭防火墙，不然会有问题[docker跨主机网络不通问题排查](..\docker consul跨主机网络不通.md)

### 1、安装consul

下载地址：https://www.consul.io/downloads.html ，安装过程见参考一和二；

### 2、启动consul

三台服务器分别运行

```shell
 # 第一台
 consul agent -server -ui -bootstrap-expect=1 -data-dir=/data/consul -node=agent-1 -client=0.0.0.0 -bind=192.168.93.128 -datacenter=dc1
 
 #第二台
 consul agent -ui -data-dir=/data/consul -node=agent-2 -client=0.0.0.0 -bind=192.168.93.129 -datacenter=dc1 -join 192.168.93.128
 
  #第三台
 consul agent -ui -data-dir=/data/consul -node=agent-2 -client=0.0.0.0 -bind=192.168.93.130 -datacenter=dc1 -join 192.168.93.128
```

此时可通过192.168.93.128(129/130):8500访问consul![image-20201017201429704](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201017201429.png)

在三台服务器上分别执行consul members，结果如图，consul搭建成功：

![image-20201017201519980](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201017201520.png)

## 二、启动docker，创建overlay网络

1、执行

```
#创建网络
docker network create -d overlay test-overlay

#查看网络
docker network ls

#创建container实例, 分别在两台服务器上创建，此时可互相ping通
docker run -itd --name test02 --network test-overlay centos
```

![image-20201017201806645](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201017201806.png)![image-20201017202009205](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201017202009.png)



