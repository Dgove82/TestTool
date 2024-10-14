import sys
from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QTabWidget,
                             QWidget, QLabel, QApplication)
from PyQt5.QtCore import Qt

from src.frontend.component.tab_func import FuncTab
from src.frontend.component.tab_temp import TempTab
from src.frontend.public import AppRoot


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # 最外层布局
        AppRoot.root = self

        self.outermost_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        self.tab_temp = TempTab()
        self.tab_sub = FuncTab()

        self.load_window()

    def load_window(self):
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
