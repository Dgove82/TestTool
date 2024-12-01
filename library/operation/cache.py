"""
用于控件缓存: 运行中产生的值
"""
import platform


class CacheElemnt:
    def __init__(self):
        self.__win = None

    @property
    def win(self):
        if self.__win is None:
            self.__win = '缓存元素'
        return self.__win


class RunInfo:
    System = None
    Version = None

    @staticmethod
    def get_system_version():
        if platform.system() == 'Windows':
            version = int(platform.version().split('.')[-1])
            if version >= 22000:
                return "Windows 11"
            else:
                return "Windows 10"


run_info = RunInfo()
