"""
控件操作方法
"""

from library.base import BasicMethod


class Element(BasicMethod):

    def set_value(self, value='1', name="good"):
        """
        设置值
        :param name: 名称
        :param value: 值
        :return:
        """
        print(value, name)

    def set_expose(self, value='1', name='good'):
        """
        设置曝光
        :param name: 名称
        :param value: 值
        :return:
        """
        print(value, name)
