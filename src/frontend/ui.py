import sys
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QTabWidget,
                             QWidget, QLabel, QApplication)
from PyQt5.QtCore import Qt
from common.tools import log
from src.frontend.component.tab_func import FuncTab
from src.frontend.component.tab_temp import TempTab
from src.frontend.component.control import LogThread, LogEditBox, KeyWatchThread
from src.frontend.public import app_root
from pynput import keyboard


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # 最外层布局
        app_root.root = self

        self.outermost_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        self.tab_temp = TempTab()
        self.tab_sub = FuncTab()
        self.log_editbox = LogEditBox()

        self.init_ui()
        self.log_info_ui()
        self.log_record_start()
        self.key_watch_start()

        self.meta_hotkey = False

    def init_ui(self):
        # 设置主窗口的标题和初始大小
        self.setWindowTitle('测试小工具')
        self.setGeometry(100, 100, 800, 600)

        # 创建一个中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 设置垂直布局
        central_widget.setLayout(self.outermost_layout)

        # 创建并添加大标题
        title_label = QLabel('测试小工具', self)
        title_label.setStyleSheet("font-size: 30pt")
        title_label.setAlignment(Qt.AlignCenter)

        self.outermost_layout.addWidget(title_label)

        # 创建分页
        self.outermost_layout.addWidget(self.tab_widget)
        self.tab_widget.setStyleSheet("""
            QTabBar::tab:selected {
                background-color: #4d85ff;
                color: white;
            }
            QTabBar::tab:!selected {
                background-color: lightgrey;
                color: black;
            }
        """)

        self.tab_widget.addTab(self.tab_sub, '方法执行')

        self.tab_widget.addTab(self.tab_temp, '临时页')

    def log_info_ui(self):
        log_layout = QVBoxLayout()
        log_label = QLabel()
        log_label.setText('运行日志:')
        self.log_editbox.setReadOnly(True)
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_editbox)
        self.outermost_layout.addLayout(log_layout)

    def log_record_start(self):
        """
        启动日志线程
        """
        app_root.ui_log = LogThread()
        app_root.ui_log.log_signal.connect(self.log_editbox.append_color_info)
        app_root.ui_log.start()
        app_root.ui_log.success('日志线程已就绪...')

    def key_watch_start(self):
        """
        启动键盘监听线程
        """
        app_root.key_watch = KeyWatchThread()
        app_root.key_watch.press_signal.connect(self.press_event)
        app_root.key_watch.release_signal.connect(self.release_event)
        while app_root.key_watch.sig != 1:
            app_root.key_watch.start()
        app_root.ui_log.success('键鼠监听线程已启动...')

    def press_event(self, key):
        if key.key == keyboard.Key.cmd:
            self.meta_hotkey = True
        elif isinstance(key.key, keyboard.KeyCode) and key.key.char == 'z' and self.meta_hotkey:
            self.normal_window()

    def release_event(self, key):
        if key.key == keyboard.Key.cmd:
            self.meta_hotkey = False

    def closeEvent(self, event):
        if app_root.ui_log.isRunning():
            app_root.ui_log.terminate()
            log.info('日志线程已关闭.')
            app_root.ui_log.wait()

        if app_root.key_watch.isRunning():
            app_root.key_watch.key_listener.stop()
            app_root.key_watch.mouse_listener.stop()
            app_root.ui_log.wait()
            app_root.ui_log.info('键鼠监听线程已关闭.')

    def mini_window(self):
        self.showMinimized()

    def normal_window(self):
        self.showNormal()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
