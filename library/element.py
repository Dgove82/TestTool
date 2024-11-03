"""
控件操作方法
"""
import time

from library.base import BasicMethod


class Element(BasicMethod):

    def set_value(self, value='1', name="good"):
        """
        【单功能】设置值设置值设置值设置值设置值设置值设置值设置值设置值设置值设置值设置值设置值设置值
        :param name: 名称
        :param value: 值
        :return:
        """
        time.sleep(10)
        print(value, name)

    def set_expose(self, value='2', name='expoese'):
        """
        【单功能】设置曝光
        :param name: 名称
        :param value: 值
        :return:
        """
        print(value, name)
