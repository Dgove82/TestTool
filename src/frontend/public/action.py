import time

from src.frontend.public import AppRoot
from src.frontend.public import control_func
from common.tools import Singleton
from src.control.center import ControlCenter
from src.frontend.component.control import ExecDialog, TaskThread
from PyQt5.QtWidgets import *


class FuncAction(Singleton):
    def __init__(self):
        self.app = AppRoot
        self.control = control_func

    def load_action(self):
        self.control.search_result_list.itemDoubleClicked.connect(lambda: self.action_step_add())
        self.control.search_result_list.customContextMenuRequested.connect(self.action_open_result_menu)
        self.control.process_list.customContextMenuRequested.connect(self.action_open_process_menu)
        self.control.reset_btn.clicked.connect(self.action_process_reset)
        self.control.exec_btn.clicked.connect(self.action_process_exec)

        self.control.search_btn.clicked.connect(self.action_search)

    def action_step_add(self):
        """
        将搜索方法添加至流程中
        """
        index = self.control.search_result_list.currentRow()
        self.control.process_list.addItem(str(index))

    def action_open_result_menu(self, position):
        """
        搜索结果右键菜单
        """
        selected_index = control_func.search_result_list.currentRow()
        self.control.right_menu.clear()
        add_action = QAction('添加: 将步骤添加至流程中')
        self.control.right_menu.addAction(add_action)
        add_action.triggered.connect(lambda: self.handle_action('step_add'))
        self.control.right_menu.setEnabled(selected_index != -1)
        self.control.right_menu.exec_(self.control.search_result_list.mapToGlobal(position))

    def action_open_process_menu(self, position):
        """
        流程结果右键菜单
        """
        selected_index = control_func.process_list.currentRow()

        self.control.right_menu.clear()
        del_action = QAction('删除: 将步骤从流程中删除')
        self.control.right_menu.addAction(del_action)
        del_action.triggered.connect(lambda: self.handle_action('step_del'))

        self.control.right_menu.setEnabled(selected_index != -1)
        self.control.right_menu.exec_(control_func.process_list.mapToGlobal(position))

    def handle_action(self, action):
        """
        处理右键菜单项
        """
        if action == 'step_add':
            self.action_step_add()
            self.control.right_menu.close()
        elif action == 'step_del':
            index = self.control.process_list.currentRow()
            self.control.process_list.takeItem(index)

    def action_conf_set(self):
        """
        程序配置设置
        """
        pass

    def action_search(self):
        """
        执行搜索
        """
        self.control.search_result_list.clear()
        search_key = self.control.search_line.text()
        ControlCenter.func_search(search_key)
        AppRoot.ui_log.info(f'搜索到{len(ControlCenter.search_record)}个方法')
        for index, func in enumerate(ControlCenter.search_record):
            line = f'{index + 1}.{func.depict_func}'
            self.control.search_result_list.addItem(line)

    def action_add_record(self):
        """
        添加录制方法
        """
        pass

    def run(self):
        for i in range(10):
            AppRoot.ui_log.info('执行中')
            time.sleep(1)

    def action_process_exec(self):
        AppRoot.ui_log.info('开始执行流程')
        self.control.run_task.start()

        self.app.dialog = ExecDialog(AppRoot.root)
        self.app.dialog.exec_()

    def action_process_reset(self):
        AppRoot.ui_log.info('流程已重置')
        self.control.process_list.clear()

    def action_read_process(self):
        """
        读取流程,从自定义文件中读取
        """
        pass

    def action_save_process(self):
        """
        将留存储存到自定义文件中
        """
        pass

    def action_generate_py(self):
        """
        生成py代码
        """
        pass
