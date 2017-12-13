# 什么是可迭代对象？其中含有__iter__方法，返回迭代器
# 什么是迭代器？

"""
1. 自定义可迭代对象
class Foo(object):

    def __init__(self,arg):
        self.arg = arg

    def __iter__(self):
        return iter([11,22,33,44,55])

obj = Foo("as")

for row in obj:
    print(row)
"""


# class Foo(object):
#
#     def __init__(self,arg):
#         self.arg = arg
#
#     def __iter__(self):
#         yield '开始'
#         for item in self.arg:
#             yield item
#         yield '结束'
# obj = Foo([11,22,33,44])
#
# # 去循环一个含有__iter__方法的对象时，会执行__iter__方法，获取返回值
# # 在进行for循环：next...
# for row in obj:
#     print(row)

# 什么是可迭代对象？其中含有__iter__方法，返回迭代器

# 什么是迭代器？ 含有__next__方法
# iter([1,2,3,4,54])

# 什么是生成器？ 函数中含有yield关键字的函数，被执行后是生成器;含有__next__方法
# def func():
#     yield 1
#     yield 2

# 什么是可迭代对象？其中含有__iter__方法，返回【迭代器;生成器】
# class Foo(object):

    # def __iter__(self):
    #     return iter([11,22,3,4])

    # def __iter__(self):
    #     yield 1
    #     yield 2
    #     yield 3


# import requests
#
#
# requests.get(
#     url='http://127.0.0.1:8001/score/1/1/'
# )
#
# requests.post(
#     url='http://127.0.0.1:8001/score/1/1/',
#     data={'username':'alex','pwd':123}
# )
#









class Foo(object):

    def __add__(self, other):
        return 999


obj1 = Foo()
obj2 = Foo()
obj3 = obj1 + obj2 # 自动触发 obj1的 __add__方法（obj2）

print(obj3)

# c = 1 + 2
# print(c)













