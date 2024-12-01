from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from src.frontend.components.tabs.tab_func import FuncTab
from src.frontend.components.tabs.tab_watch import WatchTab
from src.frontend.components.tabs.tab_pos import PosTab
from src.frontend.components.tabs.tab_db import DBTab
from src.frontend.public import app_root


class MultTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.out_layout = QVBoxLayout()

        self.mult_tab = QTabWidget()

        self.init_ui()

    def init_ui(self):
        self.setLayout(self.out_layout)
        self.out_layout.setContentsMargins(0, 0, 0, 0)
        self.out_layout.addWidget(self.mult_tab)
        self.load_style()

        tab_func = FuncTab(0)
        tab_watch = WatchTab(1)
        tab_pos = PosTab(2)
        tab_db = DBTab(3)

        self.mult_tab.addTab(tab_func, '组装车间')
        self.mult_tab.addTab(tab_watch, '操作回溯')
        self.mult_tab.addTab(tab_pos, '控件定位')
        self.mult_tab.addTab(tab_db, '设备配置')

    def load_style(self):
        self.mult_tab.setStyleSheet("""
            QTabWidget::pane {
                border-top: 1px solid #409eff;
                background-color: #ececec;
            }
            QTabWidget::tab-bar {
                alignment: left;
            }
            QTabBar {
                background-color: #F5F7FA;
            }

            QTabBar::tab {
                border: 1px solid #E4E7ED;
                background-color: #FFFFFF;
                min-width: 40px;
                padding: 5px 10px;
                color: #909399;
            }

            QTabBar::tab:selected, QTabBar::tab:hover {
                background-color: #FFFFFF;
                border-color: #409EFF;
            }

            QTabBar::tab:selected {
                border-bottom: 3px solid #409EFF;
                color: #409eff;
            }
                           """)
