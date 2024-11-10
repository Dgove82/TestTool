"""
控件操作方法
"""
import time

from library.operation.base import BasicMethod
import settings


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

    def start_record(self):
        """
        开始录制
        """
        settings.record.start_record_video(save_path=settings.Files.VIDEO_DIR)

    def stop_record(self):
        """
        结束录制
        """
        settings.record.stop_record_video()

    def sleepping(self, timeout="10"):
        """
        睡眠
        :param timeout: 睡眠时间
        """
        settings.log.info('开始睡眠')
        timeout = int(timeout)
        time.sleep(timeout)
        settings.log.info('睡眠结束')

