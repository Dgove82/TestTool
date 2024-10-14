import sys
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QTabWidget,
                             QWidget, QLabel, QApplication)
from PyQt5.QtCore import Qt

from src.frontend.component.tab_func import FuncTab
from src.frontend.component.tab_temp import TempTab
from src.frontend.component.control import LogThread, LogEditBox
from src.frontend.public import AppRoot
from common.tools import TimeTool
import settings


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # 最外层布局
        AppRoot.root = self

        self.outermost_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        self.tab_temp = TempTab()
        self.tab_sub = FuncTab()
        self.log_editbox = LogEditBox()

        self.init_ui()
        self.log_info_ui()
        self.log_record_start()

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
        AppRoot.ui_log = LogThread(log_file=f'{settings.LOG_DIR.joinpath(TimeTool.get_format_day())}.log')
        AppRoot.ui_log.log_signal.connect(self.log_editbox.append_color_info)
        AppRoot.ui_log.start()
        AppRoot.ui_log.success('日志线程已就绪...')

    def closeEvent(self, event):
        print(AppRoot.ui_log.isRunning())
        if AppRoot.ui_log.isRunning():
            AppRoot.ui_log.terminate()
            AppRoot.ui_log.wait()
        print(AppRoot.ui_log.isRunning())


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
