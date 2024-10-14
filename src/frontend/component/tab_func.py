from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from src.frontend.component.control import ExecDialog, CommonButton
from src.frontend.public.tab_func import control_func
from src.frontend.component.control import LogEditBox
from src.frontend.public.action import FuncAction


class FuncTab(QWidget):
    def __init__(self):
        super().__init__()
        # 布局
        self.tab_func_layout = QVBoxLayout()
        self.header_layout = QHBoxLayout()
        self.search_process_layout = QHBoxLayout()
        self.search_result_layout = QVBoxLayout()
        self.execute_btn_layout = QHBoxLayout()
        self.bottom_layout = QVBoxLayout()

        # 控件
        control_func.root = self
        control_func.conf_btn = CommonButton('系统参数配置')
        control_func.search_line = QLineEdit()
        control_func.search_btn = CommonButton("搜索")
        control_func.add_record_btn = CommonButton('添加录制方法')
        control_func.search_result_list = QListWidget()
        control_func.process_list = QListWidget()
        control_func.exec_btn = CommonButton('执行流程')
        control_func.reset_btn = CommonButton('重置流程')
        control_func.read_process_btn = CommonButton('读取流程')
        control_func.save_process_btn = CommonButton('保存流程')
        control_func.generate_py_btn = CommonButton('生成py')
        control_func.log_editbox = LogEditBox()
        control_func.right_menu = QMenu()

        self.init_ui()
        self.connect_action()

    def parse_layout(self):
        self.setLayout(self.tab_func_layout)
        self.tab_func_layout.addLayout(self.header_layout)
        self.tab_func_layout.addLayout(self.search_process_layout)
        self.search_process_layout.addLayout(self.search_result_layout)
        self.tab_func_layout.addLayout(self.execute_btn_layout)
        self.tab_func_layout.addLayout(self.bottom_layout)

    def init_ui(self):
        self.parse_layout()
        self.conf_setting_ui()
        self.search_action_ui()
        self.search_result_ui()
        self.func_process_ui()
        self.execute_btn_ui()
        self.log_info_ui()

    def connect_action(self):
        FuncAction().load_action()

    def conf_setting_ui(self):
        control_func.conf_btn = CommonButton('系统参数配置')
        self.header_layout.addWidget(control_func.conf_btn)

    def search_action_ui(self):
        search_layout = QHBoxLayout()
        search_label = QLabel()
        search_label.setText('搜索:')
        search_layout.addWidget(search_label)

        control_func.search_line.setPlaceholderText('请输入方法关键字')
        search_layout.addWidget(control_func.search_line)
        search_layout.addWidget(control_func.search_btn)
        search_layout.addWidget(control_func.add_record_btn)

        self.search_result_layout.addLayout(search_layout)

    def search_result_ui(self):
        """
         结果展示
         :return:
         """
        result_layout = QVBoxLayout()

        info_label = QLabel()
        info_label.setText('搜索结果:')
        result_layout.addWidget(info_label)
        result_layout.addWidget(control_func.search_result_list)

        self.search_result_layout.addLayout(result_layout)

        control_func.search_result_list.setStyleSheet("""
             QListWidget::item{
                 padding: 5px;
             }
             QListWidget::item:hover {
                 background-color: #d6eaf8;
                 color: black;   
             }
             """)
        # control_func.search_result_list.viewport().setCursor(Qt.PointingHandCursor)

        control_func.search_result_list.setContextMenuPolicy(Qt.CustomContextMenu)

    def func_process_ui(self):
        process_layout = QVBoxLayout()
        info_label = QLabel()
        info_label.setText('流程显示:')
        process_layout.addWidget(info_label)

        process_layout.addWidget(control_func.process_list)

        self.search_process_layout.addLayout(process_layout)

        control_func.process_list.setStyleSheet("""
                        QListWidget::item{
                            padding: 5px;
                        }
                        QListWidget::item:hover {
                            background-color: #d6eaf8;
                            color: black;  
                        }
                        """)
        # control_func.process_list.viewport().setCursor(Qt.PointingHandCursor)

        control_func.process_list.setContextMenuPolicy(Qt.CustomContextMenu)

    def execute_btn_ui(self):
        """
        显示 重置 / 执行
        :return:
        """
        self.execute_btn_layout.addWidget(control_func.exec_btn)
        self.execute_btn_layout.addWidget(control_func.reset_btn)
        self.execute_btn_layout.addWidget(control_func.read_process_btn)
        self.execute_btn_layout.addWidget(control_func.save_process_btn)
        self.execute_btn_layout.addWidget(control_func.generate_py_btn)

    def log_info_ui(self):
        log_layout = QVBoxLayout()
        log_label = QLabel()
        log_label.setText('执行日志:')
        control_func.log_editbox.setReadOnly(True)
        control_func.log_editbox.append('日志已就绪...\n')
        log_layout.addWidget(log_label)
        log_layout.addWidget(control_func.log_editbox)
        self.bottom_layout.addLayout(log_layout)

    def func_reset_exec(self):
        control_func.process_list.clear()
