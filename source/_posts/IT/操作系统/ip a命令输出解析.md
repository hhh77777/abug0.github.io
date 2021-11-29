# ip a命令输出解析

[引用自Docker深入浅出系列](https://www.cnblogs.com/evan-liang/p/12271468.html)

![image-20201017153823551](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201017153830.png)

`<BROADCAST,MULTICAST,UP,LOWER_UP>`这个配置串告诉我们：

> BROADCAST 该接口支持广播
> MULTICAST 该接口支持多播
> UP 网络接口已启用
> LOWER_UP 网络电缆已插入，设备已连接至网络

**其他配置信息:**

> mtu 1500 最大传输单位（数据包大小）为1,500字节
> qdisc pfifo_fast 用于数据包排队
> state UP 网络接口已启用
> group default 接口组
> qlen 1000 传输队列长度
> link/ether 08:00:27:ba:0a:28 接口的 MAC（硬件）地址
> brd ff:ff:ff:ff:ff:ff 广播地址
> inet 192.168.100.12/24 绑定的IPv4 地址
> brd 192.168.0.255 广播地址
> scope global 全局有效
> dynamic eth1 地址是动态分配的
> valid_lft 143401sec IPv4 地址的有效使用期限
> preferred_lft 143401sec IPv4 地址的首选生存期
> inet6 fe80::a00:27ff:feba:a28/64 IPv6 地址
> scope link 仅在此设备上有效
> valid_lft forever IPv6 地址的有效使用期限
> preferred_lft forever IPv6 地址的首选生存期

