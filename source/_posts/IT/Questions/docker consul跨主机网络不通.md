---
title: "docker consul跨主机网络不通"
isCJKLanguage: true
date: 2020-10-17 20:29:19
updated: 2020-10-17 20:29:19
categories: 
- IT
- Questions
tags: 
- Questions
---

# docker 跨主机overlay不通问题排查

搭建过程见[dokcer跨主机overlay网络搭建](..\Docker\Docker-consul跨主机Overlay网络搭建.md)，搭建完后发现网络不通，执行

{%spoiler 示例代码%}
```shell
journalctl -u docker.service
```
{%endspoiler%}

输出如图，明显有error，打开/var/log/messages，进一步看到是hostname冲突，

![image-20201017192949361](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201017192949.png)

![image-20201017202730128](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201017202730.png)

修改hostname，重启服务器及服务后，还是存在error,关闭firewalld，重启docker服务，输出正常，此时不同服务器上的container实例可以正常通信。

![image-20201017202829687](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20201017202829.png)