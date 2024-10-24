import traceback

import settings
from src.frontend.public import control_func, app_root
from common.tools import Singleton
from src.control.center import ControlCenter
from src.frontend.component.control import ExecDialog, FuncParamDialog, DefineParamDialog
from PyQt5.QtWidgets import *


class FuncAction(Singleton):
    def __init__(self):
        self.app = app_root
        self.control = control_func

    def load_action(self):
        self.control.search_result_list.itemDoubleClicked.connect(self.action_step_add)
        self.control.search_result_list.customContextMenuRequested.connect(self.action_open_result_menu)
        self.control.process_list.customContextMenuRequested.connect(self.action_open_process_menu)
        self.control.reset_btn.clicked.connect(self.action_process_reset)
        self.control.exec_btn.clicked.connect(self.action_process_exec)
        self.control.save_process_btn.clicked.connect(self.action_save_process)
        self.control.read_process_btn.clicked.connect(self.action_read_process)
        self.control.generate_py_btn.clicked.connect(self.action_generate_py)

        self.control.conf_btn.clicked.connect(self.action_conf_set)
        self.control.search_btn.clicked.connect(self.action_search)
        self.control.add_record_btn.clicked.connect(self.action_add_record)

        self.action_search()

    def action_step_add(self):
        index = self.control.search_result_list.currentRow()
        ControlCenter.step_click(index)

        self.app.dialog = FuncParamDialog(parent=self.app.root)

        self.app.dialog.confirm.clicked.connect(self.action_step_insert)

        self.app.dialog.exec_()

    def action_step_insert(self):
        """
        将搜索方法添加至流程中
        """
        if self.app.dialog:
            form_data = self.app.dialog.make_data()

            pos = int(form_data.pop('self_process_index')) - 1

            ControlCenter.func_step_insert(pos, form_data.get('params', '{}'))
            self.control.process_list.insertItem(pos, f'{ControlCenter.steps[pos].get("depict_func")}')
            self.app.dialog.close_dialog()

        else:
            raise

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
            ControlCenter.step_del(index)
            self.control.process_list.takeItem(index)

    def action_conf_set(self):
        """
        程序配置设置
        """
        self.app.root.mini_window()
        pass

    def action_search(self):
        """
        执行搜索
        """
        self.control.search_result_list.clear()
        search_key = self.control.search_line.text()
        ControlCenter.func_search(search_key)
        app_root.ui_log.info(f'搜索到{len(ControlCenter.search_record)}个方法')
        for index, func in enumerate(ControlCenter.search_record):
            line = f'{index + 1}.{func.depict_func}'
            self.control.search_result_list.addItem(line)

    def action_define_step_insert(self, events):
        if self.app.dialog is not None:
            self.app.dialog.running = False
            data = self.app.dialog.make_data()
            pos = int(data.get('self_process_index')) - 1
            name = data.get('name') if data.get('name') is not None else '自定义方法'
            ControlCenter.define_step_insert(events, pos, name)
            self.control.process_list.insertItem(pos, name)
            self.app.root.normal_window()
            self.app.dialog.close_dialog()
        else:
            raise

    def action_add_record(self):
        """
        添加录制方法
        """
        self.app.dialog = DefineParamDialog(self.app.root)
        # self.app.dialog.watch_thread.event_signal.connect(self.action_define_step_insert)
        if self.app.key_watch_task_insert is False:
            self.app.key_watch.event_signal.connect(self.action_define_step_insert)
            self.app.key_watch_task_insert = True
        self.app.dialog.exec_()

    def action_process_exec(self):
        self.app.ui_log.info('开始执行流程')
        self.app.root.mini_window()
        self.control.run_task.start()
        self.control.run_task.finish_signal.connect(self.action_process_finish)

        self.app.dialog = ExecDialog(self.app.root)
        self.app.dialog.exec_()

    def action_process_finish(self):
        self.app.root.normal_window()
        self.app.dialog.info_label.setText('执行完毕')

    def action_process_reset(self):
        ControlCenter.step_reset()
        if self.control.process_list.count() > 0:
            self.app.ui_log.info('流程已重置')
            self.control.process_list.clear()
        else:
            self.app.ui_log.info('流程为空，无需重置')

    def action_read_process(self):
        """
        读取流程,从自定义文件中读取
        """
        ControlCenter.steps_read()
        self.control.process_list.clear()
        for f in ControlCenter.steps:
            f_type = f.get('type', None)
            if f_type == 'exist':
                self.control.process_list.addItem(f'{f.get("depict_func", None)}')
            elif f_type == 'define':
                self.control.process_list.addItem(f'{f.get("name", None)}')
        self.app.ui_log.success(f'已从<{settings.PROCESS_PATH}>读取流程')

    def action_save_process(self):
        """
        将留存储存到自定义文件中
        """
        ControlCenter.steps_save()

    def action_generate_py(self):
        """
        生成py代码
        """
        ControlCenter.generate_py()
