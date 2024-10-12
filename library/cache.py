"""
用于控件缓存: 运行中产生的值
"""


class CacheElemnt:
    def __init__(self):
        self.__win = None

    @property
    def win(self):
        if self.__win is None:
            self.__win = '缓存元素'
        return self.__win


class RunInfo:
    Version = None
