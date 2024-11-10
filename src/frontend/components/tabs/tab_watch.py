from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class WatchTab(QWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index

        self.init_ui()

    def init_ui(self):
        watch_layout = QVBoxLayout()
        self.setLayout(watch_layout)
        tip_label = QLabel('敬请期待')
        tip_label.setStyleSheet('font-size: 60pt')
        tip_label.setAlignment(Qt.AlignCenter)
        watch_layout.addWidget(tip_label)
