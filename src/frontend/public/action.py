import json
import traceback

import settings
from src.frontend.public import control_func, app_root
from common.tools import Singleton
from src.intermediary.center import ControlCenter, handler
from src.intermediary.data_load import init_table
from src.frontend.components import (ExecDialog, FuncParamDialog, DefineParamDialog,
                                     EditParamDialog, LoadDialog,GeneratePyDialog)
from PyQt5.QtWidgets import *


class FuncAction(Singleton):
    def __init__(self):
        self.app = app_root
        self.control = control_func
        init_table()

    def load_action(self):
        self.control.search_result_list.itemDoubleClicked.connect(self.action_step_add)
        self.control.process_list.itemDoubleClicked.connect(self.action_step_edit)
        self.control.search_result_list.customContextMenuRequested.connect(self.action_open_result_menu)
        self.control.process_list.customContextMenuRequested.connect(self.action_open_process_menu)
        self.control.reset_btn.clicked.connect(self.action_process_reset)
        self.control.exec_btn.clicked.connect(self.action_process_exec)
        self.control.save_process_btn.clicked.connect(self.action_save_process)
        self.control.read_process_btn.clicked.connect(self.action_read_process)
        self.control.data_load_btn.clicked.connect(self.action_load_func)
        self.control.generate_py_btn.clicked.connect(self.action_generate_py)
        self.control.search_btn.clicked.connect(lambda: self.action_search(1))
        self.control.add_record_btn.clicked.connect(self.action_add_record)

        self.action_search()

    def action_step_add(self):
        index = self.control.search_result_list.currentRow()
        handler.step_click(index)

        self.app.dialog = FuncParamDialog(parent=self.app.root)

        self.app.dialog.confirm.clicked.connect(self.action_step_insert)
        self.app.dialog.cancel.clicked.connect(self.app.dialog.close_dialog)

        self.app.dialog.exec_()

    def action_step_insert(self):
        """
        将搜索方法添加至流程中
        """
        if self.app.dialog:
            form_data = self.app.dialog.make_data()

            pos = int(form_data.pop('self_process_index')) - 1

            handler.func_step_insert(pos, form_data.get('params', '{}'))
            # self.control.process_list.insertItem(pos, f'{ControlCenter.steps[pos].get("depict_func")}')
            self.action_flash_process()
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
        edit_action = QAction('编辑: 重新编辑参数')
        self.control.right_menu.addAction(edit_action)
        edit_action.triggered.connect(lambda: self.handle_action('step_edit'))

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
            handler.step_del(index)
            # self.control.process_list.takeItem(index)
            self.action_flash_process()
        elif action == 'step_edit':
            self.action_step_edit()
            self.control.right_menu.close()

    def action_step_edit(self):
        index = self.control.process_list.currentRow()
        ControlCenter.checked = index

        self.app.dialog = EditParamDialog(parent=self.app.root)

        self.app.dialog.confirm.clicked.connect(self.action_edit_step)
        self.app.dialog.cancel.clicked.connect(self.app.dialog.close_dialog)

        self.app.dialog.exec_()

    def action_edit_step(self):
        if self.app.dialog:
            form_data = self.app.dialog.make_data()
            func = ControlCenter.steps[ControlCenter.checked]
            temp = {}
            for key, value in form_data.items():
                if func.get('type') == 'exist':
                    temp.update({key: value})
                else:
                    self.app.ui_log.info(f'录制方法名<{func.get("name")}>更新为<{value}>')
                    func[key] = value
                    self.control.process_list.currentItem().setText(f'{ControlCenter.checked + 1}.{value}')

            if func.get('type') == 'exist':
                func["params"] = json.dumps(temp)
                self.app.ui_log.info(f'<{func.get("depict_func")}>参数更新成功')
            self.app.dialog.close_dialog()

    def action_search(self, way=0):
        """
        执行搜索
        """
        self.control.search_result_list.clear()
        search_key = self.control.search_line.text()
        handler.func_search(search_key)
        if way == 0:
            app_root.ui_log.info(f'共加载{len(ControlCenter.search_record)}个方法')
        else:
            app_root.ui_log.info(f'搜索到{len(ControlCenter.search_record)}个方法')
        for index, func in enumerate(ControlCenter.search_record):
            line = f'{index + 1}.{func.depict_func}'
            self.control.search_result_list.addItem(line)

    def action_flash_process(self):
        self.control.process_list.clear()
        for index, func in enumerate(ControlCenter.steps):
            if func.get('type') == 'exist':
                line = f'{index + 1}.{func.get("depict_func", None)}'
                self.control.process_list.addItem(line)
            else:
                line = f'{index + 1}.{func.get("name", None)}'
                self.control.process_list.addItem(line)
        ControlCenter.exec_step_end = len(ControlCenter.steps)

    def action_define_step_insert(self, events):
        if self.app.dialog is not None:
            self.app.dialog.running = False
            data = self.app.dialog.make_data()
            pos = int(data.get('self_process_index')) - 1
            name = data.get('name') if data.get('name') is not None else '自定义方法'
            handler.define_step_insert(events, pos, name)
            # self.control.process_list.insertItem(pos, name)
            self.action_flash_process()
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
        self.app.dialog = ExecDialog(self.app.root)
        self.app.dialog.exec_()

    def action_process_finish(self):
        self.app.root.normal_window()
        self.app.dialog.info_label.setText('执行完毕')

    def action_process_reset(self):
        handler.step_reset()
        if self.control.process_list.count() > 0:
            self.app.ui_log.info('流程已重置')
            self.control.process_list.clear()
        else:
            self.app.ui_log.info('流程为空，无需重置')

    def action_read_process(self):
        """
        读取流程,从自定义文件中读取
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getOpenFileName(self.app.root, "打开流程文件", str(settings.Files.PROCESS_DIR),
                                                   "JSON Files (*.json)", options=options)
        if file_path:
            handler.steps_read(file_path)
            ControlCenter.exec_step_end = len(ControlCenter.steps)
            self.control.process_list.clear()
            for index, f in enumerate(ControlCenter.steps):
                f_type = f.get('type', None)
                if f_type == 'exist':
                    self.control.process_list.addItem(f'{index + 1}.{f.get("depict_func", None)}')
                elif f_type == 'define':
                    self.control.process_list.addItem(f'{index + 1}.{f.get("name", None)}')

    def action_save_process(self):
        """
        将留存储存到自定义文件中
        """
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self.app.root, "保存流程", str(settings.Files.PROCESS_DIR),
                                                   "JSON Files (*.json)", options=options)
        if file_path:
            handler.steps_save(file_path)

    def action_load_func(self):
        self.app.dialog = LoadDialog(self.app.root)
        self.app.dialog.exec_()

    def action_generate_py(self):
        """
        生成py代码
        """
        self.app.dialog = GeneratePyDialog(self.app.root)
        self.app.dialog.exec_()