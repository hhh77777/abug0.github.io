## Linux中的虚拟网络一：tap/tun与veth

### 参考

[参考一: 云计算底层技术-虚拟网络设备：bridge（bridge decision过程、bridge与netfilter关系、vlan设备原理）](https://opengers.github.io/openstack/openstack-base-virtual-network-devices-bridge-and-vlan/)

[参考二: 云计算底层技术-虚拟网络设备：tap/tun,veth（文内包含虚机的数据流向分析）](https://opengers.github.io/openstack/openstack-base-virtual-network-devices-tuntap-veth/)

[参考三: TUN/TAP设备解析](https://www.jianshu.com/p/09f9375b7fa7)

[参考四: TUN/TAP设备收发包流程分析](https://blog.liu-kevin.com/2020/01/06/tun-tapshe-bei-qian-xi/)

[参考五: veth设备与bridge通信过程分析](https://segmentfault.com/a/1190000009491002)

[参考六: 数据包在各层间的流向分析](https://zhuanlan.zhihu.com/p/139247344)

![bridge](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084804.png)

![yDTFvEohmQfiWz5](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816163436.jpg)

### 关于参考的补充

##### 针对参考五的补充一：关于tcpdump抓包位置与网络协议栈

此处参考 [tcpdump解析](../../操作系统/tcpdump解析.md)

![tcp生效位置与网络协议栈](C:/Users/pc/Desktop/1546067532777618.png)

![iptables数据流向](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816123402.jpg)

![数据流向分析](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816124406.jpg)

![部分工具工作层次](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816124414.jpg)

##### 针对参考五的补充二：关于tap/tun设备数据包上行到协议栈的补充

![bridge](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200816084804.png)

实际上，用报文不进入协议栈这样的说法是不准确的，确切的说，应该是报文在到达设备对应的层次（tap是二层，tun是三层）后，报文会流向bridge,继而离开主机的协议栈，去往tap/tun或者其他命名空间。