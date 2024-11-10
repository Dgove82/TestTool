from PyQt5.QtWidgets import QWidget, QTabWidget, QVBoxLayout
from src.frontend.components.tabs.tab_func import FuncTab
from src.frontend.components.tabs.tab_watch import WatchTab
from src.frontend.components.tabs.tab_pos import PosTab


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

        self.mult_tab.addTab(tab_func, '组装车间')
        self.mult_tab.addTab(tab_watch, '操作回溯')
        self.mult_tab.addTab(tab_pos, '控件定位')

    def load_style(self):
        self.mult_tab.setStyleSheet("""
                               QTabWidget::pane { 
                                   border-top: 2px solid #C2C7CB;
                                   border-bottom: 2px solid #C2C7CB;
                               }
                               QTabBar::tab:selected {
                                   background-color: #4d85ff;
                                   color: white;
                               }
                               QTabBar::tab:!selected {
                                   background-color: lightgrey;
                                   color: black;
                               }
                           """)
