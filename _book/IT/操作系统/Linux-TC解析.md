# Linux流量控制工具-TC

[参考一: TC](https://tldp.org/HOWTO/Adv-Routing-HOWTO/lartc.qdisc.filters.html)

[参考二: TC文档](https://tldp.org/HOWTO/Traffic-Control-HOWTO/components.html)

 [参考三: TC中文手册](..\参考文档\LARTC-zh_CN.GB2312.pdf) 

[参考四: Linux流量控制: QoS与ToS](https://toutiao.io/posts/lpkg13/preview)

[参考五: TC实例](https://www.wsfnk.com/archives/882.html)

[参考六: HOWTO-Linux Advanced Routing & Traffic Control HOWTO](https://tldp.org/HOWTO/Adv-Routing-HOWTO/index.html)

## tc-noqueu

[tc-noqueue](http://linux-tc-notes.sourceforge.net/tc/doc/sch_noqueue.txt)

```
The noqueue queuing discipline
------------------------------

Parameters.
  None.

Classes.  The noqueue queuing discipline does not have classes.

Scheduling.  The noqueue queuing discipline has not have a scheduler.

Policing.  The noqueue queuing discipline drops all packets queued onto
it.

Rate limiting.  The noqueue queuing discipline does not rate limit
traffic.

Classifier.  The noqueue queuing discipline does not classify packets.


Comments.

- Although the noqueue queuing discipline does drop all packets
  queued onto it, in practice that never happens.  Instead when
  a packet is sent over a device it checks if it is using the
  "noqueue" discipline.  If so the device sends the packet
  immediately, or drops it if it can't be sent.  Thus the
  noqueue discipline really means "don't queue this packet".

- noqueue is the queuing discipline that is used by default
  for :virtual: devices, meaning it is the queuing discipline
  installed when a virtual device is first created.  It is
  also the queuing discipline used after you "tc qdisc del"
  another queuing discipline from a virtual device.
  
- You can _not_ manually change a queuing discipline for a
  device or class to noqueue using "tc qdisc add noqueue".  You can
  get around this for virtual devices by deleting their queuing
  discipline.  It is not possible to assign the noqueue queuing
  discipline to physical devices or classes.
```