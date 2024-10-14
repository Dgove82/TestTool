from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt5.QtCore import Qt, QObject, pyqtSignal


class LogSignal(QObject):
    log_signal = pyqtSignal(str)


class BaseDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

    def center_on_parent(self):
        if self.parent():
            parent = self.parent().frameGeometry()
            child = self.frameGeometry()
            top = parent.top() + (parent.height() - child.height()) / 2
            left = parent.left() + (parent.width() - child.width()) / 2
            self.move(left, top)


class ExecDialog(BaseDialog):
    """
    执行会话框
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        dialog_layout = QVBoxLayout()
        self.setGeometry(100, 100, 200, 100)
        self.center_on_parent()

        self.setWindowTitle('流程')
        info_label = QLabel('执行中')
        dialog_layout.addWidget(info_label)
        self.setLayout(dialog_layout)

    def closeEvent(self, event):
        print('关闭')
        event.accept()


class ParamDialog(QDialog):
    """
    参数设置会话框
    """

    def __init__(self, parent=None):
        super().__init__(parent)

    def init_ui(self):
        pass


class CommonButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def leaveEvent(self, event):
        self.unsetCursor()


class LogEditBox(QTextEdit):
    def __init__(self):
        super().__init__()
        self.setStyleSheet("""
        QTextEdit{
            background: #1e1f22;
            font-weight: bold;
            color: white;
        }
        """)

    def append_color_info(self, msg: str):
        info = msg.split('|')
        color = QColor('white')
        if len(info) > 3:
            log_type = info[2].lower()
            if 'warning' in log_type:
                color = QColor('#a58813')
            elif 'error' in log_type:
                color = QColor('#dc3d2d')
            elif 'success' in log_type:
                color = QColor('#56902a')

        document = self.document()
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.End)
        char_format = QTextCharFormat()
        char_format.setForeground(color)
        cursor.setCharFormat(char_format)
        cursor.insertText(msg)
        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
