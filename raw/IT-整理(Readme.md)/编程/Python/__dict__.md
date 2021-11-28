# Python--\__dict__

## 总结

* 实例的\__dict__只包含与实例相关的属性
* 类的\__dict__包含所有实例共享的属性和方法，例如静态属性等
  * 且不包含其父类的静态属性和方法等，但是通过该类可以直接访问这些属性和方法
* 在该类中查找不到时, hasattr和getattr会在父类的属性中查找。

## 测试代码

```python
class A:
    aa = 3

    def __init__(self) -> None:
        self.a = 1


class B(A):
    bb = 5

    def __init__(self) -> None:
        self.b = 2


class C(A):
    cc = 5

    def __init__(self) -> None:
        super().__init__()
        self.c = 2
 

if __name__ == '__main__':
    b = B()
    print(B.__dict__)
    print(getattr(B, 'aa'))
    print(B.aa)

    print(b.__dict__)
    print(b.bb)

    c = C()
    print(C.__dict__)
    print(c.__dict__)
```

运行结果：

```bash
{'__module__': '__main__', 'bb': 5, '__init__': <function B.__init__ at 0x000001D3086C8F70>, '__doc__': None}
3
3
{'b': 2}
5
{'__module__': '__main__', 'cc': 5, '__init__': <function C.__init__ at 0x000001D3086C8E50>, '__doc__': None}
{'a': 1, 'c': 2}
```



## 参考文章

[参考一: Python \__dict__与dir()区别](https://blog.csdn.net/lis_12/article/details/53521554)

[参考二: 浅谈\__dict__](https://zhuanlan.zhihu.com/p/39984987)