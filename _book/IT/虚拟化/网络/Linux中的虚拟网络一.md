# Linux中的虚拟网络一：tap/tun与veth

### 目录

[TOC]

### 参考

[参考一: 云计算底层技术-虚拟网络设备：bridge（bridge decision过程、bridge与netfilter关系、vlan设备原理）](https://opengers.github.io/openstack/openstack-base-virtual-network-devices-bridge-and-vlan/)

[参考二: 云计算底层技术-虚拟网络设备：tap/tun,veth（文内包含虚机的数据流向分析）](https://opengers.github.io/openstack/openstack-base-virtual-network-devices-tuntap-veth/)

[参考三: TUN/TAP设备解析](https://www.jianshu.com/p/09f9375b7fa7)

[参考四: TUN/TAP设备收发包流程分析](https://blog.liu-kevin.com/2020/01/06/tun-tapshe-bei-qian-xi/)

[参考五: veth设备与bridge通信过程分析](https://segmentfault.com/a/1190000009491002) 

[参考六: 数据包在各层间的流向分析](https://zhuanlan.zhihu.com/p/139247344)

[参考七: netfilter框架（iptables、netfilter处理流程及连接跟踪表）](https://opengers.github.io/openstack/openstack-base-netfilter-framework-overview/)



![bridge](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084804.png)

![yDTFvEohmQfiWz5](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816163436.jpg)

### 关于参考的补充

##### 针对参考的补充：tc、bridge check、iptables与协议栈

![netfilter](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816175903.png)

##### 针对参考五的补充一：关于tcpdump抓包位置与网络协议栈

此处参考 [tcpdump解析](../../操作系统/tcpdump解析.md)

![tcp生效位置与网络协议栈](C:/Users/pc/Desktop/1546067532777618.png)

![iptables数据流向](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816123402.jpg)

![数据流向分析](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816124406.jpg)

![部分工具工作层次](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816124414.jpg)

##### 针对参考五的补充二：关于tap/tun设备数据包上行到协议栈的补充

实际上，用报文不进入协议栈这样的说法是不准确的，确切的说，应该是报文在到达设备对应的层次（tap是二层，tun是三层）后，报文会流向bridge,继而离开主机的协议栈，去往tap/tun或者其他命名空间。

##### 针对参考六的补充：ebtables过滤未生效的思考

根据下图，在配有docker环境的centos8系统中，docker网络模式为bridge，做端口映射（通过nat）。

配置ebtables规则，前后两次实验分别是filter/forward、filter/input，动作为=drop，抓包分析来看，均未生效，容器内部皆能收到包（bridge_bf关闭与否结果一致），结论为数据包未经过ebtables filter input/forward。

在filter/output配置drop，包被丢弃，容器内未收到。

使用iptables配置规则：

* filter/forward--drop，包被丢弃，表现为容器内部收不到包；

* filter/input--drop，包未被丢弃，容器内可收到；

* filter-output--drop，未被丢弃，容器内可收到；

  根据以上实验结果，可知数据包路径：

  * INPUT PATH：bridge check后走T，进入Network Layer，直到routing decision。（走T路线的原因：外部访问时的目的IP实际为host物理网卡IP，该网卡未挂载到网桥，不属于桥设备）
  * FORWARD PATH：routing decision后，进入Link Layer；
  * OUTPUT PATH：Link Layer。

![netfilter](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816175903.png)

![bridge](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084804.png)

