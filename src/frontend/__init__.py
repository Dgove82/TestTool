import sys
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout,
                             QWidget, QLabel, QApplication, QHBoxLayout)
from PyQt5.QtCore import Qt
from src.frontend.components.tabs import MultTab
from src.frontend.components import LogThread, LogEditBox, KeyWatchThread, CommonButton, ConfDialog, TitleLabel
from src.frontend.public import app_root
from pynput import keyboard
import settings


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # 最外层布局
        app_root.root = self

        self.outermost_layout = QVBoxLayout()

        self.log_editbox = LogEditBox()

        self.init_ui()

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

        self.log_record_start()
        self.key_watch_start()
        self.header_ui()
        self.tabs_ui()
        self.log_info_ui()
        self.load_actions()

    def load_actions(self):
        app_root.conf_btn.clicked.connect(self.action_conf_set)

    def header_ui(self):
        # 顶部
        top_layout = QHBoxLayout()
        app_root.conf_btn = CommonButton("⚙")
        app_root.conf_btn.setStyleSheet("""
                    QPushButton{
                        background-color: transparent;
                        font: bold 20pt;
                        color: #839192;
                    }
                """)

        top_layout.addWidget(app_root.conf_btn)
        top_layout.setStretchFactor(app_root.conf_btn, 1)

        # 创建并添加大标题
        title_label = QLabel('测试小工具', self)
        title_label.setStyleSheet("""
                    QLabel{
                        font: bold 20pt;
                        letter-spacing: 10px;
                    }
                """)
        title_label.setAlignment(Qt.AlignCenter)
        top_layout.addWidget(title_label)
        top_layout.setStretchFactor(title_label, 10)
        top_layout.setSpacing(0)
        top_layout.addStretch(1)
        self.outermost_layout.addLayout(top_layout)

        self.outermost_layout.setStretchFactor(top_layout, 1)

    def tabs_ui(self):
        # 创建分页
        tab_widget = MultTab()
        self.outermost_layout.addWidget(tab_widget)
        self.outermost_layout.setStretchFactor(tab_widget, 20)

    def log_info_ui(self):
        log_layout = QVBoxLayout()
        log_label = TitleLabel('运行日志')
        self.log_editbox.setReadOnly(True)
        log_layout.addWidget(log_label)
        log_layout.addWidget(self.log_editbox)
        log_layout.setSpacing(0)
        self.outermost_layout.addLayout(log_layout)
        self.outermost_layout.setStretchFactor(log_layout, 10)

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

    def action_conf_set(self):
        """
        程序配置设置
        """
        app_root.dialog = ConfDialog(parent=self)

        app_root.dialog.exec_()

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
            settings.log.info('日志线程已关闭.')
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
