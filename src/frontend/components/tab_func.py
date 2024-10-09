from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from src.frontend.components.elements import TempDialog, CommonButton


class FuncTab(QWidget):
    def __init__(self):
        super().__init__()
        # 布局
        self.tab_func_layout = QVBoxLayout()

        # 控件
        self.search_line_edit = QLineEdit()
        self.search_btn = QPushButton("搜索")
        self.res_show_view = QListWidget(self)
        self.process_show_view = QListWidget(self)
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
        search_layout = QHBoxLayout()
        self.tab_func_layout.addLayout(search_layout)

        conf_btn = CommonButton('系统参数配置')
        search_layout.addWidget(conf_btn)

        search_label = QLabel()
        search_label.setText('搜索:')
        search_layout.addWidget(search_label)

        self.search_line_edit.setPlaceholderText('请输入方法关键字')
        search_layout.addWidget(self.search_line_edit)
        search_layout.addWidget(self.search_btn)

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
        process_layout = QHBoxLayout()

        info_layout = QVBoxLayout()
        info_label = QLabel()
        info_label.setText('流程显示:')
        info_layout.addWidget(info_label)
        info_layout.addWidget(self.process_show_view)

        log_layout = QVBoxLayout()
        log_label = QLabel()
        log_label.setText('执行日志:')
        editbox = QTextEdit()
        editbox.setReadOnly(True)
        editbox.append('测试信息')

        log_layout.addWidget(log_label)
        log_layout.addWidget(editbox)

        process_layout.addLayout(info_layout)
        process_layout.addLayout(log_layout)
        self.tab_func_layout.addLayout(process_layout)

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
        dialog = TempDialog(self)

        dialog.exec_()

    def func_reset_exec(self):
        self.process_show_view.clear()
