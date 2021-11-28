---
title: "magic method"
isCJKLanguage: true
date: 2021-02-21 17:53:33
updated: 2021-02-21 17:53:33
categories: 
- 编程
- Python
tags: 
- Python
---

# Magic method

## \__del__

\__del__类似于析构函数，在对象销毁时调用

### e.g. 1:

{%spoiler 示例代码%}
```python
class A:
	def __del__(self):
		print('asd')

a = A()
del a
# 会打印出asd

def f():
    a = A()

f()
# 也会打印出asd, 因为a作为局部变量, 函数结束时被销毁
```
{%endspoiler%}

note: \__del__被不是在调用del a时被调用，而是对象销毁时调用。

### e.g. 2

{%spoiler 示例代码%}
```python
class A:
	def __del__(self):
		print('asd')

a = A()
b = a

del a # 不打印asd, 因为b持有对该对象的引用, 该对象还没被销毁
del b # 打印asd, 引用变为0, 销毁对象, __del__被调用
```
{%endspoiler%}