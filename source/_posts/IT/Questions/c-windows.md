---
title: "c-windows"
isCJKLanguage: true
date: 2020-08-30 09:07:09
updated: 2020-08-30 09:07:09
categories: 
- IT
- Questions
tags: 
- Questions
---

# Questions-1 C代码编译通过无法运行

* 环境：
  * win10 64位
  * gcc

* 现象
  * gcc编译c代码通过，运行时显示无法在libmingwex中找到_emutls_get_address。

* 解决

  * 在mingw中移除mingw32-libmingwex-dev和mingw32-libmingwex-dll两个包。![image-20200830090655739](https://raw.githubusercontent.com/Abug0/Typora-Pics/master/pics/Typora20200830090702.png)