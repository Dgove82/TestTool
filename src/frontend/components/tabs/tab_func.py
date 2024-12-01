from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from src.frontend.components import (CommonButton, TitleLabel, ClickLabel, RecordListWidget, DropdownButton,
                                     CommonLineEdit, CommonMenu, CommonInfoBox)
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
        control_func.search_line = CommonLineEdit()
        control_func.search_btn = CommonButton("搜索")
        # control_func.add_record_btn = CommonButton('添加录制方法')
        control_func.add_special_func_btn = DropdownButton('添加特殊方法')
        control_func.step_btn = DropdownButton('步骤')
        control_func.process_btn = DropdownButton('流程')
        control_func.common_result_list = RecordListWidget()
        control_func.search_result_list = RecordListWidget()
        control_func.pre_read_view = CommonInfoBox("请选择方法")
        control_func.process_list = RecordListWidget()
        control_func.exec_btn = CommonButton('执行流程')
        control_func.arrow_btn = ClickLabel('➡')
        control_func.data_load_btn = CommonButton('重载方法')
        control_func.generate_py_btn = CommonButton('生成用例脚本')
        control_func.right_menu = CommonMenu()

        control_func.actions = FuncAction()

        self.init_ui()
        control_func.actions.load_action()

        self.drag_action()

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
        search_label = TitleLabel('搜索栏')
        search_layout.addWidget(search_label)

        control_func.search_line.setPlaceholderText('请输入方法关键字')
        search_layout.addWidget(control_func.search_line)
        search_layout.addWidget(control_func.search_btn)
        # search_layout.addWidget(control_func.add_record_btn)
        search_layout.addWidget(control_func.add_special_func_btn)
        self.specatial_btn_menu_ui()

        self.search_result_layout.addLayout(search_layout)

    def search_result_ui(self):
        """
         结果展示
         :return:
         """
        out_result_layout = QHBoxLayout()
        # 搜索结果展示的布局
        result_layout = QVBoxLayout()

        common_label = TitleLabel('常用方法')
        result_layout.addWidget(common_label)
        control_func.common_result_list.setFixedHeight(120)
        result_layout.addWidget(control_func.common_result_list)

        info_label = TitleLabel('搜索结果')
        result_layout.addWidget(info_label)
        result_layout.addWidget(control_func.search_result_list)
        result_layout.setSpacing(0)

        # control_func.search_result_list.viewport().setCursor(Qt.PointingHandCursor)

        pre_read_layout = QVBoxLayout()

        # control_func.pre_read_view.setWordWrap(True)
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
        self.search_process_layout.addWidget(control_func.arrow_btn)

    def func_process_ui(self):
        process_layout = QVBoxLayout()

        process_btn_layout = QHBoxLayout()
        process_btn_layout.addWidget(control_func.exec_btn)
        self.step_btn_menu_ui()
        process_btn_layout.addWidget(control_func.step_btn)
        process_btn_layout.addWidget(control_func.process_btn)
        self.process_btn_menu_ui()
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

        # control_func.process_list.viewport().setCursor(Qt.PointingHandCursor)

        process_button_layout = QHBoxLayout()
        process_button_layout.addWidget(control_func.generate_py_btn)
        process_layout.addLayout(process_button_layout)

    def specatial_btn_menu_ui(self):
        control_func.add_special_func_btn.add_menu_action('添加录制方法')
        control_func.add_special_func_btn.add_menu_action('添加循环方法')

    def step_btn_menu_ui(self):
        control_func.step_btn.add_menu_action('导入')
        control_func.step_btn.add_menu_action('导出')

    def process_btn_menu_ui(self):
        control_func.process_btn.add_menu_action('重置')
        control_func.process_btn.add_menu_action('导入')
        control_func.process_btn.add_menu_action('导出')

    def drag_action(self):
        control_func.common_result_list.setDragDropMode(QListWidget.DragOnly)
        control_func.search_result_list.setDragDropMode(QListWidget.DragOnly)
        control_func.process_list.setDragDropMode(QListWidget.DragDrop)

        control_func.common_result_list.dragEnterEvent = self.dragEnterEvent
        control_func.search_result_list.dragEnterEvent = self.dragEnterEvent
        control_func.process_list.dragEnterEvent = self.dragEnterEvent
        control_func.common_result_list.dropEvent = self.dropEvent
        control_func.search_result_list.dropEvent = self.dropEvent
        control_func.process_list.dropEvent = self.dropEvent

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        if event.source() == control_func.common_result_list or event.source() == control_func.search_result_list:
            target_index = control_func.process_list.indexAt(event.pos())
            if target_index.isValid():
                control_func.actions.action_step_add(target_index.row() + 1)
            else:
                control_func.actions.action_step_add()
        elif event.source() == control_func.process_list:
            source_index = control_func.process_list.currentRow()
            target_index = control_func.process_list.indexAt(event.pos())
            if target_index.isValid():
                control_func.actions.action_step_update_order(source_index, target_index.row())
        else:
            event.ignore()
