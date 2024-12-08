from PyQt5.QtWidgets import *
from PyQt5.QtGui import QTextCursor, QColor, QTextCharFormat, QPixmap, QIcon, QFont, QSyntaxHighlighter
from PyQt5.QtCore import Qt, pyqtSignal, QSize, QRegularExpression
import settings
import os


class RecordListWidget(QListWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_stylesheet()

    def init_stylesheet(self):
        self.setStyleSheet("""
             QListWidget {
                border: none; /* 移除边框 */
                background-color: #ffffff; /* 背景颜色 */
                color: #606266; /* 默认文本颜色 */
                outline: 0; /* 移除焦点时的边框 */
            }
            QListWidget::item {
                border-bottom: 1px solid #e4e7ed; /* 底部分隔线 */
                padding: 10px; /* 内边距 */
            }
            QListWidget::item:hover {
                background-color: #f5f7fa; /* 鼠标悬停时的背景颜色 */
                color: #409eff; /* 鼠标悬停时的文本颜色 */
            }
            QListWidget::item:selected {
                background-color: #ecf5ff; /* 选中时的背景颜色 */
                color: #409eff; /* 选中时的文本颜色 */
                border: none; /* 移除选中时的边框 */
            }
            QListWidget::item:selected:hover {
                background-color: #d9ecff; /* 选中且鼠标悬停时的背景颜色 */
                color: #409eff; /* 选中且鼠标悬停时的文本颜色 */
            }
           
             """)
        self.setContextMenuPolicy(Qt.CustomContextMenu)


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


class CommonScrollArea(QScrollArea):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_stylesheet()

    def init_stylesheet(self):
        self.setStyleSheet("""
                    QScrollArea {
                        background-color: transparent;
                    }
                    QScrollArea > QWidget > QWidget {
                        background-color: white;
                    }
                    QScrollBar:vertical {
                        background: #e7e8e9;
                        width: 12px;
                        margin: 0px 0px 0px 0px;
                    }
                    QScrollBar::handle:vertical {
                        background: #c2c3c4;
                        min-height: 20px;
                    }
                    QScrollBar::add-line:vertical {
                        background: #c2c3c4;
                        height: 0px;
                        subcontrol-position: bottom;
                        subcontrol-origin: margin;
                    }
                    QScrollBar::sub-line:vertical {
                        background: #c2c3c4;
                        height: 0px;
                        subcontrol-position: top;
                        subcontrol-origin: margin;
                    }
                    QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                        background: none;
                    }
                    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                        background: none;
                    }
                """)


class CommonButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMouseTracking(True)  # Ensure mouse tracking is enabled
        self.initStyle()

    def initStyle(self):
        self.setStyleSheet("""
                QPushButton {
                    border: 1px solid #DCDFE6;
                    background-color: #FFFFFF;
                    padding: 10px 15px;
                    border-radius: 4px;
                    color: #606266;
                }
                QPushButton:hover {
                    border-color: #C0C4CC;
                    background-color: #ECF5FF;
                    color: #409EFF;
                }
                QPushButton:pressed {
                    border-color: #3A8EE6;
                    background-color: #E1F3FF;
                }
            """)

    def enterEvent(self, event):
        self.setCursor(Qt.PointingHandCursor)

    def leaveEvent(self, event):
        self.unsetCursor()


class CommonInfoBox(QTextEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #DCDFE6;
                border-radius: 4px;
                padding: 10px;
                background-color: #f4f4f5;
                color: #606266;
                font-size: 13pt;
            }
        """)
        self.setReadOnly(True)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

    def show_context_menu(self, position):
        context_menu = CommonMenu(self)
        copy_action = context_menu.addAction("复制")
        all_action = context_menu.addAction("全选")
        action = context_menu.exec_(self.mapToGlobal(position))
        if action == copy_action:
            self.copy()
        elif action == all_action:
            self.selectAll()


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
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.show_context_menu)

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
        cursor.insertText(f'{info[0]:^19}')

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
        cursor.insertText(f'{info[2]:^9}|{"".join(info[3:])}')

        self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())

    def show_context_menu(self, position):
        context_menu = CommonMenu(self)
        clear_action = context_menu.addAction("清空")
        copy_action = context_menu.addAction("复制")
        all_action = context_menu.addAction("全选")
        action = context_menu.exec_(self.mapToGlobal(position))
        if action == clear_action:
            self.clear()
        elif action == copy_action:
            self.copy()
        elif action == all_action:
            self.selectAll()


class CommonLineEdit(QLineEdit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_style()

    def init_style(self):
        # 设置Element UI风格的样式
        self.setStyleSheet("""
            QLineEdit {
                border: 1px solid #dcdfe6; /* 边框颜色 */
                border-radius: 4px; /* 边框圆角 */
                padding: 6px 10px; /* 内边距 */
                background-color: #fff; /* 背景颜色 */
                color: #606266; /* 文本颜色 */
                font-size: 14px; /* 字体大小 */
            }
            QLineEdit:hover {
                border-color: #c0c4cc; /* 鼠标悬停时的边框颜色 */
            }
            QLineEdit:focus {
                border-color: #409eff; /* 获得焦点时的边框颜色 */
            }
        """)


class TitleLabel(QLabel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_ui()

    def init_ui(self):
        self.setStyleSheet("""
                    QLabel {
                        color: #606266;
                        background-color: #f4f4f5; 
                        padding: 10px 15px;
                        border: 1px solid #dcdfe6;
                    }
                """)
        self.setAlignment(Qt.AlignLeft)


class NoAutoScrollTreeWidget(QTreeWidget):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_style()

    def scrollTo(self, index, hint=...):
        pass

    def init_style(self):
        self.setStyleSheet("""
         QTreeWidget {
             background-color: #FFFFFF; /* Element UI 背景色 */
             border: none;
             outline: none;
         }
         QTreeWidget::item {
             padding: 5px;
             border-bottom: 1px solid #EBEEF5; /* Element UI 分隔线颜色 */
         }
         QTreeWidget::item:hover {
             background-color: #F5F7FA; /* Element UI 鼠标悬停背景色 */
         }
         QTreeWidget::item:selected {
             color: #FFFFFF; /* Element UI 选中项文本颜色 */
             background-color: #409EFF; /* Element UI 选中项背景色 */
         }
         QHeaderView::section {
             background-color: #DCDFE6; /* Element UI 头部背景色 */
             color: #909399; /* Element UI 头部文本颜色 */
             padding: 5px;
             border: 1px solid #DCDFE6; /* Element UI 头部边框 */
         }
         """)


class CssTableView(QTableView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_style()

    def init_style(self):
        self.setStyleSheet("""
            QTableView {
                background-color: #FFFFFF; /* Element UI 背景颜色 */
                border: none; /* 无边框 */
                border-radius: 4px; /* 圆角边框 */
                gridline-color: #EBEEF5; /* Element UI 分隔线颜色 */
            }
            QTableView::item {
                color: #606266; /* Element UI 文本颜色 */
                border-bottom: 1px solid #EBEEF5; /* 行底边框 */
            }
            QTableView::item:hover {
                background-color: #F5F7FA; /* Element UI 鼠标悬停背景颜色 */
            }
            QTableView::item:selected {
                background-color: #409EFF; /* Element UI 选中项背景颜色 */
            }
            QTableView::item:selected:hover {
                background-color: #66B1FF; /* Element UI 选中项鼠标悬停背景颜色 */
            }
            QTableView::item:alternate {
                background-color: #FAFAFA; /* Element UI 交替行背景颜色 */
            }
            QHeaderView {
                background-color: #FFFFFF; /* Element UI 头部背景颜色 */
                border: none; /* 无边框 */
                border-bottom: 1px solid #EBEEF5; /* 底部边框 */
            }
            QHeaderView::section {
                color: #909399; /* Element UI 头部文本颜色 */
                background-color: #FFFFFF; /* Element UI 头部背景颜色 */
                padding: 5px; /* 内边距 */
                border: none; /* 无边框 */
                border-bottom: 1px solid #EBEEF5; /* 底部边框 */
            }
            QHeaderView::section:first {
                border-right: 1px solid #EBEEF5; /* 添加表头顶部分隔线 */
            }
            QHeaderView::section:checked {
                color: #409EFF; /* Element UI 选中头部文本颜色 */
                background-color: #F5F7FA; /* Element UI 选中头部背景颜色 */
            }
                """)
        # 隐藏垂直头
        self.verticalHeader().setVisible(False)
        self.setAlternatingRowColors(True)


class DropdownButton(CommonButton):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = CommonMenu(self)
        self.setMenu(self.menu)
        # self.menu.triggered.connect(self.onMenuTriggered)
        self.set_arrow_icon(f'{os.path.join(settings.DEPS_PROGRAM, "assets/arrow.png")}')
        self.setStyleSheet(self.styleSheet() + "QPushButton::menu-indicator { image: none; }")

    def resizeEvent(self, event):
        # self.menu.setMinimumWidth(self.width())
        self.menu.setFixedWidth(self.width())
        super().resizeEvent(event)

    def set_arrow_icon(self, icon_path):
        # 加载图标
        pixmap = QPixmap(icon_path)
        # 设置图标
        self.setIcon(QIcon(pixmap))
        # 设置图标大小
        self.setIconSize(QSize(22, 16))  # 根据需要调整图标大小
        self.setLayoutDirection(Qt.RightToLeft)

    def add_menu_action(self, text):
        action = QAction(text, self)
        self.menu.addAction(action)


class CommonMenu(QMenu):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.init_style()
        # self.setMinimumWidth(self.parent().sizeHint().width())

    def init_style(self):
        self.setStyleSheet("""
            QMenu {
                border-radius: 4px;
                background-color: #FFF;
                color: #606266;
            }
            QMenu::item {
                padding: 10px 20px;
                border: none;
                color: #606266;
                background-color: transparent;
            }
            QMenu::item:selected {
                color: #409EFF;
                background-color: #ECF5FF;
                border-radius: 4px;
            }
            QMenu::separator {
                height: 1px;
                background-color: #DCDFE6;
                margin-left: 10px;
                margin-right: 10px;
            }
            QMenu::item:disabled { 
                color: #C0C4CC;
                background-color: transparent; 
            }
                """)


class DarculaHighlighter(QSyntaxHighlighter):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.highlightingRules = []

        # Keyword format
        keywordFormat = QTextCharFormat()
        keywordFormat.setForeground(QColor("#CC7832"))
        keywordFormat.setFontWeight(QFont.Bold)
        keywordPatterns = [
            r'\bFalse\b', r'\bNone\b', r'\bTrue\b', r'\band\b', r'\bas\b', r'\bassert\b',
            r'\bbreak\b', r'\bclass\b', r'\bcontinue\b', r'\bdef\b', r'\bdel\b', r'\belif\b',
            r'\belse\b', r'\bexcept\b', r'\bfinally\b', r'\bfor\b', r'\bfrom\b', r'\bglobal\b',
            r'\bif\b', r'\bimport\b', r'\bin\b', r'\bis\b', r'\blambda\b', r'\bnonlocal\b',
            r'\bnot\b', r'\bor\b', r'\bpass\b', r'\braise\b', r'\breturn\b', r'\btry\b',
            r'\bwhile\b', r'\bwith\b', r'\byield\b'
        ]
        self.highlightingRules.extend([(QRegularExpression(pattern), keywordFormat) for pattern in keywordPatterns])

        # Function and class name format
        functionNameFormat = QTextCharFormat()
        functionNameFormat.setForeground(QColor("#56a7f5"))  # Adjusted color
        functionNamePattern = QRegularExpression(
            r'\b[A-Za-z_][A-Za-z0-9_]*\b(?=\()')  # Only highlight names followed by '('
        self.highlightingRules.append((functionNamePattern, functionNameFormat))

        # Number format
        numberFormat = QTextCharFormat()
        numberFormat.setForeground(QColor("#6897BB"))
        self.highlightingRules.append((QRegularExpression(r'\b\d+\b'), numberFormat))

        # String format
        stringFormat = QTextCharFormat()
        stringFormat.setForeground(QColor("#6A8759"))
        self.highlightingRules.append((QRegularExpression(r'"[^"\\]*(\\.[^"\\]*)*"'), stringFormat))
        self.highlightingRules.append((QRegularExpression(r"'[^'\\]*(\\.[^'\\]*)*'"), stringFormat))

        # Comment format
        commentFormat = QTextCharFormat()
        commentFormat.setForeground(QColor("#808080"))
        self.highlightingRules.append((QRegularExpression(r'#.*'), commentFormat))

        # Operator format
        operatorFormat = QTextCharFormat()
        operatorFormat.setForeground(QColor("#E8BF6A"))  # Adjusted color
        operatorPatterns = [
            r'\+', r'-', r'\*', r'/', r'//', r'%', r'==', r'!=', r'>', r'<', r'>=', r'<=', r'\+=', r'-=', r'\*=', r'/=',
            r'&', r'\|', r'\^', r'~', r'<<', r'>>'
        ]
        self.highlightingRules.extend([(QRegularExpression(pattern), operatorFormat) for pattern in operatorPatterns])

        # Symbol format
        symbolFormat = QTextCharFormat()
        symbolFormat.setForeground(QColor("#7CFC00"))  # Adjusted color
        symbolPatterns = [
            r'\(', r'\)', r'\[', r'\]'
        ]
        self.highlightingRules.extend([(QRegularExpression(pattern), symbolFormat) for pattern in symbolPatterns])

        # hide format
        hideFormat = QTextCharFormat()
        hideFormat.setForeground(QColor("#FF00FF"))  # Adjusted color
        hidePattern = QRegularExpression(
            r'\b__.*__')  # Only highlight names followed by '('
        self.highlightingRules.append((hidePattern, hideFormat))

        # self format
        selfFormat = QTextCharFormat()
        selfFormat.setForeground(QColor("#94558d"))  # Adjusted color
        selfPatterns = [
            r'self', r'super'
        ]
        self.highlightingRules.extend([(QRegularExpression(pattern), selfFormat) for pattern in selfPatterns])

    def highlightBlock(self, text):
        for pattern, format in self.highlightingRules:
            matchIterator = pattern.globalMatch(text)
            while matchIterator.hasNext():
                match = matchIterator.next()
                self.setFormat(match.capturedStart(), match.capturedLength(), format)


class CodeEditBox(QTextEdit):
    def __init__(self, parent=None):
        super(CodeEditBox, self).__init__(parent)
        self.setStyleSheet("""
            QTextEdit {
                border: 1px solid #3C3F41;
                border-radius: 4px;
                padding: 10px;
                background-color: #2B2B2B;
                color: #FFFFFF;
            }
            QTextEdit:focus {
                border-color: #528BFF;
            }
        """)
        self.highlighter = DarculaHighlighter(self.document())
