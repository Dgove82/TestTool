from PyQt5.QtWidgets import QDialog, QLabel, QVBoxLayout, QPushButton
from PyQt5.QtCore import Qt


class TempDialog(QDialog):
    """
    临时会话框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        dialog_layout = QVBoxLayout()
        info_label = QLabel('执行中')
        dialog_layout.addWidget(info_label)
        self.setLayout(dialog_layout)


class CommonButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def leaveEvent(self, event):
        self.unsetCursor()
