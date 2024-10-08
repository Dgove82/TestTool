import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel, QLineEdit, QPushButton, QListWidget,
    QScrollArea, QListView, QMenu, QAction, QHBoxLayout, QListWidgetItem
)
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # 设置主窗口的标题和初始大小
        self.setWindowTitle('测试小工具')
        self.setGeometry(100, 100, 600, 400)

        # 创建一个中心窗口
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # 创建一个垂直布局
        main_layout = QVBoxLayout(central_widget)

        # 创建并添加大标题
        title_label = QLabel('测试小工具', self)
        title_label.setStyleSheet("font-size: 30pt")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)

        sub_layout = QHBoxLayout()

        main_layout.addLayout(sub_layout)

        # 创建并添加搜索栏
        search_label = QLabel('搜索栏', self)
        sub_layout.addWidget(search_label)

        self.search_line_edit = QLineEdit(self)
        self.search_line_edit.setPlaceholderText('请输入方法关键字')
        sub_layout.addWidget(self.search_line_edit)

        # 创建并添加搜索按钮
        search_button = QPushButton('搜索', self)
        sub_layout.addWidget(search_button)

        # 创建并添加滚动区域以包含ListView
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.listView = QListView(self)
        self.scroll_area.setWidget(self.listView)
        main_layout.addWidget(self.scroll_area)

        # 创建并添加添加步骤按钮
        add_step_button = QPushButton('添加步骤', self)
        main_layout.addWidget(add_step_button)

        # 创建并添加ListWidget
        self.listWidget = QListWidget(self)
        self.listWidget.setContextMenuPolicy(Qt.CustomContextMenu)
        self.listWidget.customContextMenuRequested.connect(self.open_menu)
        main_layout.addWidget(self.listWidget)

        # 添加元素
        self.add_items_to_list_widget(['方法1', '方法2'])

        # 创建并添加执行和保存流程的按钮
        execute_button = QPushButton('执行流程', self)
        save_button = QPushButton('保存流程', self)
        main_layout.addWidget(execute_button)
        main_layout.addWidget(save_button)

    def open_menu(self, position):
        # 创建右键菜单
        menu = QMenu()
        delete_action = QAction('删除步骤', self)
        config_action = QAction('重新配置方法参数', self)
        menu.addAction(delete_action)
        menu.addAction(config_action)

        # 连接信号
        delete_action.triggered.connect(lambda: self.handle_menu_action('delete'))
        config_action.triggered.connect(lambda: self.handle_menu_action('config'))

        # 在鼠标位置显示菜单
        menu.exec_(self.listWidget.viewport().mapToGlobal(position))

    def handle_menu_action(self, action):
        if action == 'delete':
            print('执行删除')
            # 删除选中的步骤
            for item in self.listWidget.selectedItems():
                self.listWidget.takeItem(self.listWidget.row(item))
        elif action == 'config':
            # 重新配置方法参数（这里需要进一步实现）
            print("重新配置方法参数")

    def add_items_to_list_widget(self, items):
        # 循环添加元素到 QListWidget
        for item in items:
            list_item = QListWidgetItem(item)
            self.listWidget.addItem(list_item)


# 创建应用程序和主窗口
app = QApplication(sys.argv)
window = MainWindow()
window.show()

# 运行应用程序
sys.exit(app.exec_())
