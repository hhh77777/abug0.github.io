---
title: "Python垃圾回收机制"
isCJKLanguage: true
date: 2021-11-28 20:35:42
updated: 2021-11-28 20:35:42
categories: 
- 编程
- Python
tags: 
- Python
---

# Python-垃圾回收机制

Python 使用引用计数的方式管理内存，为了解决循环引用的问题又引入了标记-清除和分代回收机制。

## 引用计数

### 介绍

Python为每个对象都维护了一个引用计数器：

{%spoiler 示例代码%}
```c
typedef struct _object {
    _PyObject_HEAD_EXTRA
    Py_ssize_t ob_refcnt;
    PyTypeObject *ob_type;
} PyObject;
```
{%endspoiler%}

程序运行过程中更新ob_refcnt的值，引用计数降为0的时候释放对象（如果还对象内部持有对其他对象的引用，则还需要递减这些对象的引用计数）(cpython/Include/object.h line 439)：

{%spoiler 示例代码%}
```c
static inline void _Py_DECREF(
#ifdef Py_REF_DEBUG
    const char *filename, int lineno,
#endif
    PyObject *op)
{
#ifdef Py_REF_DEBUG
    _Py_RefTotal--;
#endif
    if (--op->ob_refcnt != 0) {
#ifdef Py_REF_DEBUG
        if (op->ob_refcnt < 0) {
            _Py_NegativeRefcount(filename, lineno, op);
        }
#endif
    }
    else {
        _Py_Dealloc(op);
    }
}
```
{%endspoiler%}

### 优缺点

优点：

* 简单
* 实时性好，可以立即释放无用对象，且分摊了垃圾收集的时间

缺点：

* 循环引用问题
* 成本：假如一个容器对象内部持有大量其他对象的引用，那么释放该容器的时候需要遍历容器内部所有对象，处理其引用计数



### 循环引用

看一段示例代码：

{%spoiler 示例代码%}
```python
import sys

l1 = []
l2 = []

l1.append(l2)
l2.append(l1)

sys.getrefcount(l1) # 输出3，比预期多一
sys.getrefcount(l2) # 输出3

del l1
sys.getrefcount(l2[0]) # 输出2
sys.getrefcount(l2)    # 输出3
```
{%endspoiler%}

解释：为什么getrefcount显示的引用是3，而不是2：

> `sys.``getrefcount`(*object*)
>
> 返回 *object* 的引用计数。返回的计数通常比预期的多一，因为它包括了作为 [`getrefcount()`](https://docs.python.org/zh-cn/3/library/sys.html#sys.getrefcount) 参数的这一次（临时）引用。

示例中l1与l2相互引用，在执行del l1后，预期的l2引用计数应当是1，但结果显示仍旧是2（getrefcount的输出减一才是此刻实际的引用计数）。

原因：del l1会将l1对象的引用计数减一，但减一后，引用计数为1，对象不会被销毁，因而不会递减它所持有的其他对象的引用计数，于是l2的引用计数依然是2。这就是循环引用问题。

## 标记-清除

Python使用标记-清除算法来解决循环引用问题。

主要过程（cpython/Modules/gcmodule.c line 1069 deduce_unreachable）：

> 1. Copy all reference counts to a different field (gc_prev is used to hold
>
>   this copy to save memory).
>
> 2. Traverse all objects in "base" and visit all referred objects using
>
>   "tp_traverse" and for every visited object, subtract 1 to the reference
>
>   count (the one that we copied in the previous step). After this step, all
>
>   objects that can be reached directly from outside must have strictly positive
>
>   reference count, while all unreachable objects must have a count of exactly 0.
>
> 3. Identify all unreachable objects (the ones with 0 reference count) and move
>
>   them to the "unreachable" list. This step also needs to move back to "base" all
>
>   objects that were initially marked as unreachable but are referred transitively
>
>   by the reachable objects (the ones with strictly positive reference count).

* 1、将链表中每个对象的引用数复制到gc_ref字段；

* 2、遍历链表中的对象，将当前对象内部引用的对象的计数减一。这一步执行后，依然存在外部变量引用的对象计数大于0，而只在其他对象内部引用的对象计数等于0；

* 3、识别出不可达对象（引用计数等于0），移到不可达链表中。被可达对象持有引用的对象也要从不可达链表中移除。

  网络图片：

  ![preview](https://pic2.zhimg.com/v2-d7314ead6b303f08a91687577c045585_r.jpg)



### 问题

每次进行标记-清除回收对象的时候，都会暂停整个应用程序，因此，标记-清除检测的频率设置就变得十分重要，也正因此，又引入了分代回收机制。

## 分代回收

分代回收建立于标记-清除的基础之上。空间换时间。

分代回收的目的是对垃圾回收检测的频率进行控制。

Python中分为三代：从0代到3代，扫描间隔越来越长。

每次扫描某代的时候，比其更年轻的代也会被扫描。

## 参考

[[1] 官网文档: 对象、类型和引用计数](https://docs.python.org/zh-cn/3/c-api/intro.html#objects-types-and-reference-counts)

[[2] Python垃圾回收机制！非常实用](https://zhuanlan.zhihu.com/p/83251959)

[[3] [整理]Python垃圾回收机制--完美讲解!](https://www.jianshu.com/p/1e375fb40506)

[[4] Python Developer's Guide: Design of CPython’s Garbage Collector](https://devguide.python.org/garbage_collector)

[[5] Python 进阶：浅析「垃圾回收机制」](https://cloud.tencent.com/developer/article/1509068)

[[6]《深度剖析CPython解释器》28. Python内存管理与垃圾回收(第二部分)：源码解密Python中的垃圾回收机制](https://www.cnblogs.com/traditional/p/13698244.html)

[[7] Python 源码阅读 - 垃圾回收机制](https://wklken.me/posts/2015/09/29/python-source-gc.html)