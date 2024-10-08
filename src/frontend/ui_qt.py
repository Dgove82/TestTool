import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt, QFile, QTextStream


class App(QMainWindow):
    def __init__(self):
        super().__init__()
        # 最外层布局

        self.outest_layout = QVBoxLayout()

        self.tab_widget = QTabWidget()

        self.tab_temp = TempTab()
        self.tab_sub = FuncTab()

        self.load_window()
        # self.load_qss()

    def load_window(self):
        # 设置主窗口的标题和初始大小
        self.setWindowTitle('测试小工具')
        self.setGeometry(100, 100, 800, 600)

        # 创建一个中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 设置垂直布局
        central_widget.setLayout(self.outest_layout)

        # 创建并添加大标题
        title_label = QLabel('测试小工具', self)
        title_label.setStyleSheet("font-size: 30pt")
        title_label.setAlignment(Qt.AlignCenter)

        self.outest_layout.addWidget(title_label)

        # 创建分页
        self.outest_layout.addWidget(self.tab_widget)
        self.tab_widget.setStyleSheet("""
            QTabBar::tab:selected {
                background-color: #4d85ff;
                color: white;
            }
            QTabBar::tab:!selected {
                background-color: lightgrey;
                color: black;
            }
        """)

        self.tab_widget.addTab(self.tab_sub, '方法执行')

        self.tab_widget.addTab(self.tab_temp, '临时页')


class SubDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        dialog_layout = QVBoxLayout()
        info_label = QLabel('执行中')
        dialog_layout.addWidget(info_label)
        self.setLayout(dialog_layout)


class FuncTab(QWidget):
    def __init__(self):
        super().__init__()
        # 布局
        self.tab_func_layout = QVBoxLayout()

        # 控件
        self.search_line_edit = QLineEdit()
        self.search_btn = QPushButton("搜索")
        self.res_show_view = QListWidget()
        self.process_show_view = QListWidget()
        self.exec_btn = QPushButton('执行流程')
        self.reset_btn = QPushButton('重置流程')
        self.read_cache_btn = QPushButton('读取流程')
        self.save_cache_btn = QPushButton('保存流程')
        self.generate_btn = QPushButton('生成py')

        self.init_ui()

    def init_ui(self):
        self.func_search()
        self.func_show_result()
        self.func_show_process()
        self.func_execute_part()

    def func_search(self):
        """
        方法搜索部分
        :return:
        """
        self.setLayout(self.tab_func_layout)
        info_layout = QHBoxLayout()
        self.tab_func_layout.addLayout(info_layout)

        search_label = QLabel()
        search_label.setText('搜索:')
        info_layout.addWidget(search_label)

        self.search_line_edit.setPlaceholderText('请输入方法关键字')
        info_layout.addWidget(self.search_line_edit)
        info_layout.addWidget(self.search_btn)

    def func_show_result(self):
        """
        结果展示
        :return:
        """
        info_label = QLabel()
        info_label.setText('搜索结果:')
        self.tab_func_layout.addWidget(info_label)
        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.res_show_view)
        self.tab_func_layout.addWidget(scroll_area)
        for i in range(100):
            self.show_res_additem(str(i))

        self.res_show_view.setStyleSheet("""
            QListWidget::item{
                padding: 5px;
            }
            QListWidget::item:hover {
                background-color: #d6eaf8;
                color: black;   
            }
            """)
        self.res_show_view.viewport().setCursor(Qt.PointingHandCursor)

        self.res_show_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.res_show_view.customContextMenuRequested.connect(self.open_show_res_menu)

        self.res_show_view.itemDoubleClicked.connect(lambda: self.handle_show_res_action('add'))

    def show_res_additem(self, item):
        """
        向结果列表中添加值
        :param item:
        :return:
        """
        self.res_show_view.addItem(item)

    def open_show_res_menu(self, position):
        """
        结果展示中的右键菜单
        :param position:
        :return:
        """
        menu = QMenu()
        add_action = QAction('添加: 将步骤添加至流程中')
        menu.addAction(add_action)

        # 信号连接
        add_action.triggered.connect(lambda: self.handle_show_res_action('add'))

        menu.exec_(self.res_show_view.mapToGlobal(position))

    def handle_show_res_action(self, action):
        if action == 'add':
            # 获取搜索中选中的索引
            index = self.res_show_view.currentRow()
            print(index)
            self.process_additem(str(index))

    def func_show_process(self):
        info_label = QLabel()
        info_label.setText('流程显示:')
        self.tab_func_layout.addWidget(info_label)
        self.tab_func_layout.addWidget(self.process_show_view)

        self.process_show_view.setStyleSheet("""
                QListWidget::item{
                    padding: 5px;
                }
                QListWidget::item:hover {
                    background-color: #d6eaf8;
                    color: black;  
                }
                """)
        self.process_show_view.viewport().setCursor(Qt.PointingHandCursor)

        self.process_show_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.process_show_view.customContextMenuRequested.connect(self.open_process_menu)

        self.process_additem('3')

    def process_additem(self, item):
        self.process_show_view.addItem(item)

    def open_process_menu(self, position):
        selected_index = self.process_show_view.currentRow()

        menu = QMenu()

        delete_action = QAction('删除: 将步骤从流程中删除')
        menu.addAction(delete_action)

        # 信号连接
        delete_action.triggered.connect(lambda: self.handle_process_action('delete'))

        menu.setEnabled(selected_index != -1)

        menu.exec_(self.process_show_view.mapToGlobal(position))

    def handle_process_action(self, action):
        if action == 'delete':
            # 获取搜索中选中的索引
            index = self.process_show_view.currentRow()
            print(index)
            self.process_show_view.takeItem(index)

    def func_execute_part(self):
        """
        显示 重置 / 执行
        :return:
        """
        control_layout = QHBoxLayout()
        self.tab_func_layout.addLayout(control_layout)
        control_layout.addWidget(self.exec_btn)
        self.exec_btn.clicked.connect(self.func_exec_exec)
        control_layout.addWidget(self.reset_btn)
        self.reset_btn.clicked.connect(self.func_reset_exec)
        control_layout.addWidget(self.read_cache_btn)
        control_layout.addWidget(self.save_cache_btn)
        control_layout.addWidget(self.generate_btn)

    def func_exec_exec(self):
        dialog = SubDialog(self)

        dialog.exec_()

    def func_reset_exec(self):
        self.process_show_view.clear()


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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec_())
