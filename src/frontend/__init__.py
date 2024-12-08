import os
import sys
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout,
                             QWidget, QApplication, QAction)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from src.frontend.components.tabs import MultTab
from src.frontend.components import LogThread, LogEditBox, KeyWatchThread, CommonButton, ConfDialog, TitleLabel
from src.frontend.public import app_root, control_func
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
        self.setWindowTitle('DS-T')
        self.setWindowIcon(QIcon(os.path.join(settings.DEPS_PROGRAM, 'assets', 'icon.png')))
        self.setGeometry(100, 100, 1000, 1000)

        # 创建一个中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 设置垂直布局
        central_widget.setLayout(self.outermost_layout)
        self.outermost_layout.setContentsMargins(0, 0, 0, 0)
        self.outermost_layout.setSpacing(5)

        self.log_record_start()
        self.key_watch_start()
        self.top_menu_ui()
        self.tabs_ui()
        self.log_info_ui()
        self.load_actions()
        self.setStyleSheet("""
                    QMainWindow {
                        background-color: #E5EAF3; 
                    }
                """ + self.styleSheet())

    def load_actions(self):
        app_root.conf_act.triggered.connect(self.action_conf_set)

    def top_menu_ui(self):
        # 创建一个菜单栏
        menubar = self.menuBar()

        # 添加菜单
        conf_menu = menubar.addMenu('设置')
        about_menu = menubar.addMenu('关于')
        self.setStyleSheet("""
                                QMenuBar {
                                    color: #606266;
                                    background-color: #DCDCDC;
                                }
                                QMenu{
                                    border: none;
                                    background-color: #FFF;
                                    color: #606266;
                                }
                                QMenu::item {
                                    padding: 4px;
                                    border: none;
                                    color: #606266;
                                    background-color: transparent;
                                }
                                QMenu::item:selected {
                                    color: #409EFF;
                                    background-color: #ECF5FF;
                                }
                                """)
        # 添加一个菜单项
        app_root.conf_act = QAction('程序配置')
        conf_menu.addAction(app_root.conf_act)
        app_root.update_info_act = QAction('更新日志')
        about_menu.addAction(app_root.update_info_act)

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

    def keyPressEvent(self, event):
        if event.key() != Qt.Key_Escape:
            if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
                # 搜索快捷键
                if control_func.root.index == control_func.root.parent().currentIndex():
                    control_func.actions.action_search(1)
            super().keyPressEvent(event)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
