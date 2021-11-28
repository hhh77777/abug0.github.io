---
title: "Celery task.update_state"
isCJKLanguage: true
date: 2021-01-10 15:08:33
updated: 2021-01-10 15:08:33
categories: 
- IT
- Celery
tags: 
- Celery
---

# Celery task.update_state

环境: python2.7 + Celery 4.3.0

## 问题描述

1、直接调用闭包函数update_task_progress（内部调用task.update_task）更新celery task state，运行正常；

2、启动新线程调用同一函数，出现报错信息:

{%spoiler 示例代码%}
```python
Exception in thread Thread-1:
Traceback (most recent call last):
  File "/usr/lib64/python2.7/threading.py", line 812, in __bootstrap_inner
    self.run()
  File "/var/lib/proj/utils/thread.py", line 36, in run
    self.__fun(*self.__args, **self.__kwargs)
  File "/var/lib/proj/test/base.py", line 84, in progress_call_back
    update_task_progress(task, percentage, desc, finished, failed, total)
  File "/var/lib/proj/utils/error.py", line 200, in update_task_progress
    task.update_state(state = 'PROGRESS', meta={'percentage': percentage, 'desc':task_desc, 'finished': finished, 'failed': failed, 'total': total})
  File "/var/lib/proj/env/lib64/python2.7/site-packages/celery-4.3.0-py2.7.egg/celery/app/task.py", line 937, in update_state
    self.backend.store_result(task_id, meta, state, **kwargs)
  File "/var/lib/proj/env/lib64/python2.7/site-packages/celery-4.3.0-py2.7.egg/celery/backends/rpc.py", line 202, in store_result
    routing_key, correlation_id = self.destination_for(task_id, request)
  File "/var/lib/proj/env/lib64/python2.7/site-packages/celery-4.3.0-py2.7.egg/celery/backends/rpc.py", line 182, in destination_for
    'RPC backend missing task request for {0!r}'.format(task_id))
RuntimeError: RPC backend missing task request for None
```
{%endspoiler%}

## 一、问题定位

追踪问题代码，首先定位到celery/backends/rpc.py Exception的抛出点:

```python
def destination_for(self, task_id, request):
        """Get the destination for result by task id.

        Returns:
            Tuple[str, str]: tuple of ``(reply_to, correlation_id)``.
        """
        # Backends didn't always receive the `request`, so we must still
        # support old code that relies on current_task.
        try:
            request = request or current_task.request
        except AttributeError:
            raise RuntimeError(
                'RPC backend missing task request for {0!r}'.format(task_id))
        return request.reply_to, request.correlation_id or task_id
{%spoiler 示例代码%}
```

此处捕获到了AttributeError，说明current_task中没有属性request，且根据报错信息，task_id为None。

根据异常日志继续向上追溯destination_for的调用者，在同一文件中，

```
{%endspoiler%}python
def store_result(self, task_id, result, state,
                     traceback=None, request=None, **kwargs):
        """Send task return value and state."""
        routing_key, correlation_id = self.destination_for(task_id, request)
        if not routing_key:
            return
        with self.app.amqp.producer_pool.acquire(block=True) as producer:
            producer.publish(
                self._to_result(task_id, state, result, traceback, request),
                exchange=self.exchange,
                routing_key=routing_key,
                correlation_id=correlation_id,
                serializer=self.serializer,
                retry=True, retry_policy=self.retry_policy,
                declare=self.on_reply_declare(task_id),
                delivery_mode=self.delivery_mode,
            )
        return result
{%spoiler 示例代码%}
```

继续向上追溯，到达celery/app/task.py，update_state的源码：

```
{%endspoiler%}python
def update_state(self, task_id=None, state=None, meta=None, **kwargs):
        """Update task state.

        Arguments:
            task_id (str): Id of the task to update.
                Defaults to the id of the current task.
            state (str): New state.
            meta (Dict): State meta-data.
        """
        if task_id is None:
            task_id = self.request.id
        self.backend.store_result(task_id, meta, state, request=self.request, **kwargs)
{%spoiler 示例代码%}
```

![image-20210104201257230](https://i.loli.net/2021/01/06/npmHTvEw3GOWNit.png)

添加日志如上图，观察self、self.request和self.request.id的值，发现self.request和self.request.id都是None：

![image-20210104201415387](https://i.loli.net/2021/01/06/TphePK8UnbvutRV.png)

同样的方法追踪current_task的值，发现current_task为None。

## 二、current_task分析

找到current_task的定义位置，在celery/_state.py  line 144：

```
{%endspoiler%}python
#: Proxy to current task.
current_task = Proxy(get_current_task)  
{%spoiler 示例代码%}
```

先看get_current_task的定义，celery/_state.py line 123：

```
{%endspoiler%}python
def get_current_task():
    """Currently executing task."""
    return _task_stack.top
{%spoiler 示例代码%}
```

继续看_task_stack的定义，celery/_state.py line 75：

```
{%endspoiler%}python
_task_stack = LocalStack()
{%spoiler 示例代码%}
```

LocalStack：栈，线程隔离

全局搜索_task_stack，发现在celery/app/tasks.py line 388，class Task中：

```
{%endspoiler%}python
def __call__(self, *args, **kwargs):
        _task_stack.push(self)
        self.push_request(args=args, kwargs=kwargs)
        try:
            return self.run(*args, **kwargs)
        finally:
            self.pop_request()
            _task_stack.pop()
{%spoiler 示例代码%}
```

综上来看，task在被调用的时候，Task对象（self）压入栈，current_task为栈顶元素，且_task_stack栈为线程隔离的，所以在新线程中调用的时候，会发现current_task为None。

## 三、思考

### 1、使用LocalStack的原因：

* 线程安全，防止多线程情景下task取值相互干扰，保证每个线程内部current_task的正确性。
* 使用LocalStack封装Local：同一线程内，可能存在多个task。

### 2、使用LocalProxy的原因：

```
{%endspoiler%}python
from celery.utils.threads import LocalStack
from celery.local import Proxy
from celery._state import get_current_task, _task_stack
from celery import current_task

def get_task():
	return _task_stack.top

_task_stack.push(12)
_task_stack.push(34)

a = get_task()
# a为34, 且赋值后不会再改变
print(a) # 34

_task_stack.push(45)
print(a) # 34, 没有变化

a_proxy = Proxy(get_task)
print(a_proxy) # 45

_task_stack.push('asd')
print(a_proxy) # 'asd',被更新了
{%spoiler 示例代码%}
```

由此可见，相对于

```
{%endspoiler%}python
current_task = get_current_task()
```

Proxy实现了动态更新的效果，确保每次访问current_task的时候，都是当前在执行的task。否则，访问了错误的task可能会导致程序异常。

但是，为什么不每次调用get_current_task？



[参考，官方回答: Task state can not be updated from within a thread when using RPC](https://github.com/celery/celery/issues/5100)

[参考一: LocalStack的使用及详解](https://blog.csdn.net/JENREY/article/details/86615508)

[参考二: Local,LocalStack,LocalProxy深入解析](https://hustyichi.github.io/2018/08/22/LocalProxy-in-flask/)

[参考四: LocalProxy解析及使用原因](https://www.jianshu.com/p/3f38b777a621)

[参考五: Flask的上下文机制：Local/LocalProxy](https://www.lagou.com/lgeduarticle/74823.html)

[参考六: Flask的上下文机制: 为什么使用LocalStack和LocalProxy](https://cizixs.com/2017/01/13/flask-insight-context/)

[参考七: Celery local.proxy的一段注释](https://segmentfault.com/q/1010000006826944)