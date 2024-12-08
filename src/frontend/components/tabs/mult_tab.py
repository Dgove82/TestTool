from PyQt5.QtWidgets import QWidget, QVBoxLayout
from src.frontend.components.tabs import register_tabs
from src.frontend.components import CommonTab
from src.frontend.public import app_root


class MultTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.out_layout = QVBoxLayout()

        app_root.mult_tab = CommonTab()

        self.init_ui()

    def init_ui(self):
        self.setLayout(self.out_layout)
        self.out_layout.setContentsMargins(0, 0, 0, 0)
        self.out_layout.addWidget(app_root.mult_tab)
        self.load_tabs()

    def load_tabs(self):
        for index, obj in enumerate(getattr(register_tabs, 'load_order')):
            tab = obj(index)
            app_root.mult_tab.addTab(tab, tab.name)
