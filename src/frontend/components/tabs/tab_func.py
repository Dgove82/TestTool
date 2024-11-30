from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from src.frontend.components import CommonButton, TitleLabel, ClickLabel
from src.frontend.public import control_func
from src.frontend.public.action import FuncAction


class FuncTab(QWidget):
    def __init__(self, index, parent=None):
        super().__init__(parent)
        self.index = index
        # 布局
        self.tab_func_layout = QVBoxLayout()
        self.search_process_layout = QHBoxLayout()
        self.search_result_layout = QVBoxLayout()
        self.execute_btn_layout = QHBoxLayout()

        # 控件
        control_func.root = self
        control_func.search_line = QLineEdit()
        control_func.search_btn = CommonButton("搜索")
        control_func.add_record_btn = CommonButton('添加录制方法')
        control_func.search_result_list = QListWidget()
        control_func.pre_read_view = QLabel("请选择方法")
        control_func.process_list = QListWidget()
        control_func.exec_btn = CommonButton('执行流程')
        control_func.reset_btn = CommonButton('重置流程')
        control_func.read_process_btn = CommonButton('读取流程')
        control_func.save_process_btn = CommonButton('保存流程')
        control_func.arrow_btn = ClickLabel('➡')
        control_func.data_load_btn = CommonButton('重载方法')
        control_func.generate_py_btn = CommonButton('生成用例脚本')
        control_func.right_menu = QMenu()

        control_func.actions = FuncAction()

        self.init_ui()
        control_func.actions.load_action()

    def parse_layout(self):
        self.setLayout(self.tab_func_layout)
        self.tab_func_layout.addLayout(self.search_process_layout)
        self.search_process_layout.addLayout(self.search_result_layout)
        self.search_process_layout.setStretchFactor(self.search_result_layout, 7)
        self.tab_func_layout.addLayout(self.execute_btn_layout)
        self.tab_func_layout.setContentsMargins(5, 5, 5, 0)
        self.tab_func_layout.setSpacing(5)

    def init_ui(self):
        self.parse_layout()
        self.search_action_ui()
        self.search_result_ui()
        self.result_bottom_ui()
        self.func_sperate_ui()
        self.func_process_ui()

    def search_action_ui(self):
        search_layout = QHBoxLayout()
        search_label = QLabel('搜索:')
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
        out_result_layout = QHBoxLayout()
        # 搜索结果展示的布局
        result_layout = QVBoxLayout()

        # info_label = QLabel()
        # info_label.setText('搜索结果:')
        info_label = TitleLabel('搜索结果')
        result_layout.addWidget(info_label)
        result_layout.addWidget(control_func.search_result_list)
        result_layout.setSpacing(0)

        control_func.search_result_list.setStyleSheet("""
             QListWidget::item{
                 padding: 5px; 
             }
             QListWidget::item:hover {
                 background-color: #e5e7e9;
                 color: black;  
             }
             QListWidget::item:selected {
                background-color: #e5e7e9;  
                color: black;  
            }
            QListWidget::item:selected:hover {
                background-color: #e5e7e9; 
                color: black;  
            }
             """)
        # control_func.search_result_list.viewport().setCursor(Qt.PointingHandCursor)

        control_func.search_result_list.setContextMenuPolicy(Qt.CustomContextMenu)

        pre_read_layout = QVBoxLayout()
        tip_label = TitleLabel('预览窗口')
        pre_read_layout.addWidget(tip_label)
        pre_read_layout.setStretchFactor(tip_label, 1)

        control_func.pre_read_view.setStyleSheet("""
            QLabel{
                border: 1px solid grey;
                background-color: white;
                font-size: 16px;
            }
        """)
        control_func.pre_read_view.setAlignment(Qt.AlignLeft)
        control_func.pre_read_view.setWordWrap(True)
        pre_read_layout.addWidget(control_func.pre_read_view)
        pre_read_layout.setStretchFactor(control_func.pre_read_view, 100)
        pre_read_layout.setSpacing(0)

        out_result_layout.addLayout(result_layout)
        out_result_layout.setStretchFactor(result_layout, 7)
        out_result_layout.addLayout(pre_read_layout)
        out_result_layout.setStretchFactor(pre_read_layout, 3)
        self.search_result_layout.addLayout(out_result_layout)

    def result_bottom_ui(self):
        result_button_layout = QHBoxLayout()
        result_button_layout.addWidget(control_func.data_load_btn)
        self.search_result_layout.addLayout(result_button_layout)

    def func_sperate_ui(self):
        # framespate = QLabel('➡')
        # framespate.setStyleSheet("""
        #     QLabel{
        #         color: #3498db;
        #         font-size: 20px;
        #     }
        # """)
        self.search_process_layout.addWidget(control_func.arrow_btn)

    def func_process_ui(self):
        process_layout = QVBoxLayout()

        process_btn_layout = QHBoxLayout()
        process_btn_layout.addWidget(control_func.exec_btn)
        process_btn_layout.addWidget(control_func.reset_btn)
        process_btn_layout.addWidget(control_func.save_process_btn)
        process_btn_layout.addWidget(control_func.read_process_btn)
        process_btn_layout.setSpacing(5)

        process_layout.addLayout(process_btn_layout)

        process_res_layout = QVBoxLayout()

        info_label = TitleLabel('流程显示')
        process_res_layout.addWidget(info_label)

        process_res_layout.addWidget(control_func.process_list)
        process_res_layout.setSpacing(0)
        process_layout.setSpacing(5)
        process_layout.addLayout(process_res_layout)

        self.search_process_layout.addLayout(process_layout)
        self.search_process_layout.setStretchFactor(process_layout, 3)

        control_func.process_list.setStyleSheet("""
                                QListWidget::item{
                                     padding: 5px;  
                                 }
                                 QListWidget::item:hover {
                                     background-color: #e5e7e9;
                                     color: black;  
                                 }
                                 QListWidget::item:selected {
                                    background-color: #e5e7e9; 
                                    color: black;   
                                }
                                QListWidget::item:selected:hover {
                                    background-color: #e5e7e9; 
                                    color: black;  
                                }
                                """)
        # control_func.process_list.viewport().setCursor(Qt.PointingHandCursor)

        control_func.process_list.setContextMenuPolicy(Qt.CustomContextMenu)

        process_button_layout = QHBoxLayout()
        process_button_layout.addWidget(control_func.generate_py_btn)
        process_layout.addLayout(process_button_layout)
