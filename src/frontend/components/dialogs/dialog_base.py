from PyQt5.QtWidgets import QDialog
from src.frontend.public import app_root
from PyQt5.QtCore import Qt


class BaseDialog(QDialog):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    def init_ui(self):
        pass

    def center_on_parent(self):
        if self.parent():
            parent = self.parent().frameGeometry()
            child = self.frameGeometry()
            top = parent.top() + (parent.height() - child.height()) / 2
            left = parent.left() + (parent.width() - child.width()) / 2
            self.move(left, top)

    def close_dialog(self):
        app_root.dialog = None
        self.accept()

    def closeEvent(self, event):
        app_root.dialog = None

    def keyPressEvent(self, event):
        if event.key() != Qt.Key_Escape:
            super().keyPressEvent(event)
