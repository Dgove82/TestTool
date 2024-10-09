from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt


class TempTab(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        temp_layout = QVBoxLayout()
        self.setLayout(temp_layout)
        tip_label = QLabel('敬请期待')
        tip_label.setStyleSheet('font-size: 60pt')
        tip_label.setAlignment(Qt.AlignCenter)
        temp_layout.addWidget(tip_label)
