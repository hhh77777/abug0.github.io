---
title: "metaclass"
isCJKLanguage: true
date: 2021-11-28 20:35:42
updated: 2021-11-28 20:35:42
categories: 
- IT
- Python
tags: 
- Python
---

# python元类--MetaClass

## 总结

类是对实例的抽象，元类是对类的描述。

使用metaclass关键字指定类的元类。

元类的实例对应的就是类。

## 测试代码

{%spoiler 示例代码%}
```python
class TestMetaClass(type):
    meta = 'Hello'

    def __new__(cls, name, bases, attrs):
        print(cls.__name__)
        print(name)
        print(dir(cls))
        if name == 'SubTest':
            nw = type.__new__(cls, name, bases, attrs)
            print(getattr(nw, 'metaaa'))
        attrs['metaaa'] = 'TestMetaClass'
        print("attrs::::::::\n", attrs)
        print(bases)
        object.__call__
        print("=================")
        return type.__new__(cls, name, bases, attrs)

    def __init__(self, *args, **kwargs):
        print("************init***********************")
        print(args)
        print('asd')


class Test(metaclass=TestMetaClass):
    name = 'Test'

    def __init__(cls):
        cls.a = 123
        print('Test---init===')


class SubTest(Test):
    sub = True
    pass


if __name__ == '__main__':
    print("++++++++++")
    t = Test()
    print(t.__module__)
    print(dir(t))

    print(dir(SubTest))

```
{%endspoiler%}

运行结果：

{%spoiler 示例代码%}
```bash
TestMetaClass
Test
['__abstractmethods__', '__base__', '__bases__', '__basicsize__', '__call__', '__class__', '__delattr__', '__dict__', '__dictoffset__', '__dir__', '__doc__', '__eq__', '__flags__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__instancecheck__', '__itemsize__', '__le__', '__lt__', '__module__', '__mro__', '__name__', '__ne__', '__new__', '__prepare__', '__qualname__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasscheck__', '__subclasses__', '__subclasshook__', '__text_signature__', '__weakrefoffset__', 'meta', 'mro']
attrs::::::::
 {'__module__': '__main__', '__qualname__': 'Test', 'name': 'Test', '__init__': <function Test.__init__ at 0x00000282B4633D30>, 'metaaa': 'TestMetaClass'}
()
=================
************init***********************
('Test', (), {'__module__': '__main__', '__qualname__': 'Test', 'name': 'Test', '__init__': <function Test.__init__ at 0x00000282B4633D30>, 'metaaa': 'TestMetaClass'})
asd
TestMetaClass
SubTest
['__abstractmethods__', '__base__', '__bases__', '__basicsize__', '__call__', '__class__', '__delattr__', '__dict__', '__dictoffset__', '__dir__', '__doc__', '__eq__', '__flags__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__instancecheck__', '__itemsize__', '__le__', '__lt__', '__module__', '__mro__', '__name__', '__ne__', '__new__', '__prepare__', '__qualname__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasscheck__', '__subclasses__', '__subclasshook__', '__text_signature__', '__weakrefoffset__', 'meta', 'mro']
TestMetaClass
attrs::::::::
 {'__module__': '__main__', '__qualname__': 'SubTest', 'sub': True, 'metaaa': 'TestMetaClass'}
(<class '__main__.Test'>,)
=================
************init***********************
('SubTest', (<class '__main__.Test'>,), {'__module__': '__main__', '__qualname__': 'SubTest', 'sub': True, 'metaaa': 'TestMetaClass'})
asd
++++++++++
Test---init===
__main__
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'a', 'metaaa', 'name']
['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'metaaa', 'name', 'sub']
```
{%endspoiler%}

## [一点细节]

参数attrs仅包含该类中定义的属性和方法，不包括从其父类中继承的属性和方法。