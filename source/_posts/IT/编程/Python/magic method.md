---
title: "magic method"
isCJKLanguage: true
date: 2021-11-28 20:35:42
updated: 2021-11-28 20:35:42
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

## 属性访问相关

\__getitem__

\__setitem__

\__delitem__

{%spoiler 示例代码%}
```python
class A:
    def __init__(self) -> None:
        self.a = 123
        self.b = 56

    def __getitem__(self, item):
        return getattr(self, item)

    def __setitem__(self, item, value):
        setattr(self, item, value)

    def __delitem__(self, item):
        delattr(self, item)


a = A()
print(a.a)
print(a['a'])

a.c = 78
print(a.__dict__)
print(a.c)
print(a['c'])

a['d'] = 100
print(a.__dict__)
print(a.d)
print(a['d'])
print(dir(a))

del a.d
print(dir(a))
```
{%endspoiler%}



## 迭代器相关

\__iter__: 返回一个迭代器对象

\__next__: 进行迭代操作

{%spoiler 示例代码%}
```python
class A:
    def __init__(self, val=None) -> None:
        self.val = val

    def __iter__(self):
        return AIterator(self)

    def __next__(self):
        return self.val


class AIterator:
    def __init__(self, src) -> None:
        self.idx = 0
        self.src = src

    def __iter__(self):
        pass

    def __next__(self):
        self.idx += 1
        if self.idx > len(self.src.val):
            raise StopIteration
        return self.src.val[self.idx-1]


a = A('1234567')
ai = iter(a)
print(next(ai))
print(next(ai))
print(next(ai))


for c in a:
    print(c)

```
{%endspoiler%}



## 上下文管理器

\__enter__

\__exit__

## 参考文章

[Python学习【魔术方法】](https://cloud.tencent.com/developer/article/1570579)