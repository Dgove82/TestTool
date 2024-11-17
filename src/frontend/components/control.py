from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat
from PyQt5.QtCore import Qt, pyqtSignal


class ClickLabel(QLabel):
    # 定义一个信号，当点击事件发生时发出
    clicked = pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QLabel{
                color: #3498db;
                font-size: 20px;
            }
        """)
        self.setFixedHeight(20)

    def mousePressEvent(self, event):
        # 当鼠标点击时发出信号
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def leaveEvent(self, event):
        self.unsetCursor()


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
            font-size: 13px;
        }
        """)

    def append_color_info(self, msg: str):
        info = msg.split('|')
        time_color = QColor('#00CC99')
        # msg = f'{info[0]:^23}|{info[2]:^11}|{"".join(info[3:])}'
        document = self.document()
        cursor = QTextCursor(document)
        cursor.movePosition(QTextCursor.End)

        # 插入时间
        time_format = QTextCharFormat()
        time_format.setForeground(time_color)
        cursor.setCharFormat(time_format)
        cursor.insertText(f'{info[0]:^23}')

        # 插入线条
        line_format = QTextCharFormat()
        line_format.setForeground(QColor('white'))
        cursor.setCharFormat(line_format)
        cursor.insertText('| ')

        # 插入log
        color = QColor('#CCCCCC')
        if len(info) > 3:
            log_type = info[2].lower()
            if 'warning' in log_type:
                color = QColor('#FFFF33')
            elif 'error' in log_type:
                color = QColor('#FF0000')
            elif 'success' in log_type:
                color = QColor('#33FF33')
            elif 'debug' in log_type:
                color = QColor('#66FFFF')
            elif 'critical' in log_type:
                color = QColor('#990000')

        log_format = QTextCharFormat()
        log_format.setForeground(color)
        cursor.setCharFormat(log_format)
        cursor.insertText(f'{info[2]:^11}|{"".join(info[3:])}')

        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())


class TitleLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
                        QLabel {
                              color: black;
                              background-color: #cccccc;
                              font: bold 14px;
                              padding: 5px;
                           }
                        """)


class NoAutoScrollTreeWidget(QTreeWidget):
    def scrollTo(self, index, hint=...):
        pass


class CssTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_style()

    def init_style(self):
        self.setStyleSheet("""
                    QTableView {
                        alternate-background-color: #E8E8E8;
                        gridline-color: #C0C0C0;
                    }
                    QTableView::item:hover {
                        background-color: #F0F0F0;
                    }
                    QTableView::item:selected {
                        color: #FFFFFF;
                        background-color: #0064C8;
                    }
                    QHeaderView::section {
                        background-color: #D0D0D0;
                        border: 1px solid #C0C0C0;
                    }
                """)
        # 隐藏垂直头
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)
